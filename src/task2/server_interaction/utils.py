import json


def parse_map_from_dict(d):
    if 'points' in d and 'lines' in d and 'name' in d:
        return Graph(d['points'], d['lines'], d['name'])
    return d


def parse_map_to_dict(obj):
    if isinstance(obj, Graph):
        d = dict()
        d['points'] = obj.points
        d['lines'] = obj.edges
        d['name'] = obj.name
        return d
    else:
        raise TypeError(
            f"Object of type '{obj.__class__.__name__}' is not JSON serializable")


def graph_from_json_file(filename):
    with open(filename) as f:
        return json.load(f, object_hook=parse_map_from_dict)


def graph_from_json_string(json_data):
    return json.loads(json_data, object_hook=parse_map_from_dict)


def buildings_from_json_string(json_data):
    return json.loads(json_data)


def graph_to_json(obj, filename):
    with open(filename) as f:
        json.dump(obj, filename, default=parse_map_to_dict)