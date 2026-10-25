"""Offline handler/persistence smoke tests (NOT an HTTP/Flask integration test).
Usage: python tests/verify.py codebase_a|codebase_b|codebase_a_refactored
If Flask is installed it still uses this test-only shim to avoid dependency on
HTTP contexts; separate live integration testing is recommended.
"""
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parents[1]
variant = sys.argv[1] if len(sys.argv) > 1 else 'codebase_a'
if variant not in {'codebase_a', 'codebase_b', 'codebase_a_refactored'}:
    raise SystemExit('Use codebase_a, codebase_b or codebase_a_refactored')

class DummyRequest:
    payload = {}

    def get_json(self, silent=True):
        return self.payload

class DummyFlask:
    def __init__(self, name):
        self.name = name

    def get(self, pattern):
        return lambda func: func

    def post(self, pattern):
        return lambda func: func

    def run(self, debug=False):
        raise RuntimeError('Install Flask to launch the real server')

request = DummyRequest()
flask_shim = types.ModuleType('flask')
flask_shim.Flask = DummyFlask
flask_shim.request = request
flask_shim.jsonify = lambda value: value
sys.modules['flask'] = flask_shim
sys.path.insert(0, str(ROOT / variant))

with tempfile.TemporaryDirectory() as temporary:
    os.environ['SEM_DB_PATH'] = str(Path(temporary) / 'test.db')
    app = importlib.import_module('app')
    results = []

    def check(label, actual, expected):
        passed = actual == expected
        results.append({'test': label, 'passed': passed, 'actual': actual})
        if not passed:
            raise AssertionError(f'{label}: expected={expected!r}, actual={actual!r}')

    def invoke(func, payload, *args):
        request.payload = payload
        raw = func(*args)
        return raw if isinstance(raw, tuple) else (raw, 200)

    check('materials catalogue', invoke(app.list_materials, {})[0],
          {'rates_rm_per_kg': {'paper': 0.5, 'plastic': 0.8, 'metal': 1.2, 'ewaste': 2.5}})
    check('quote paper 2 kg', invoke(app.quote, {'item_type': 'paper', 'weight_kg': 2}),
          ({'item_type': 'paper', 'weight_kg': 2, 'estimated_reward_rm': 1.0}, 200))
    check('quote plastic 2.5 kg', invoke(app.quote, {'item_type': 'Plastic', 'weight_kg': 2.5}),
          ({'item_type': 'plastic', 'weight_kg': 2.5, 'estimated_reward_rm': 2.0}, 200))
    check('quote missing material', invoke(app.quote, {'weight_kg': 2}),
          ({'error': 'Invalid item_type'}, 400))
    check('quote unsupported material', invoke(app.quote, {'item_type': 'glass', 'weight_kg': 2}),
          ({'error': 'Unsupported item_type'}, 400))
    check('quote negative weight', invoke(app.quote, {'item_type': 'paper', 'weight_kg': -1}),
          ({'error': 'Invalid weight_kg'}, 400))
    check('quote string weight', invoke(app.quote, {'item_type': 'paper', 'weight_kg': '2'}),
          ({'error': 'Invalid weight_kg'}, 400))
    booking = {'user_id': 7, 'item_type': 'paper', 'weight_kg': 2,
               'address': 'Putrajaya', 'pickup_date': '2026-11-02'}
    check('create booking', invoke(app.create_booking, booking),
          ({'booking_id': 1, 'estimated_reward_rm': 1.0, 'status': 'pending'}, 201))
    check('retrieve booking', invoke(app.get_booking, {}, 1),
          ({'id': 1, 'user_id': 7, 'item_type': 'paper', 'weight_kg': 2,
            'address': 'Putrajaya', 'pickup_date': '2026-11-02',
            'estimated_reward_rm': 1.0, 'status': 'pending'}, 200))
    check('missing booking 404', invoke(app.get_booking, {}, 999),
          ({'error': 'Booking not found'}, 404))
    check('invalid booking address', invoke(app.create_booking, {**booking, 'address': ' '}),
          ({'error': 'Invalid address'}, 400))
    check('invalid pickup date', invoke(app.create_booking, {**booking, 'pickup_date': '2026-02-30'}),
          ({'error': 'Invalid pickup_date'}, 400))
    print(json.dumps({'variant': variant, 'passed': len(results),
                      'tests': [{'name': r['test'], 'passed': r['passed']} for r in results],
                      'actual_results': [r['actual'] for r in results]}, indent=2))
