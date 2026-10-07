"""
simlab: tooling around the simulator rig.

`records`      a telemetry sample with both timestamps, and a JSONL recorder format
`mock_source`  replays a synthetic session as a stream, so you can build the whole
               chain before the rig exists
`latency`      a SimPy skeleton of acquisition, transport and processing delay
"""
