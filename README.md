# Apographe

- ἀπογραφή: a register or list of lands or property
- gazetteer: a geographic dictionary or index

## Getting started

Assumes an activated python 3.10.2 or greater virtual environment. 

```
pip install -U git+https://github.com/isawnyu/apographe.git
```

Then you can do stuff like:

```python
Python 3.10.2 (main, Jan 28 2022, 15:08:24) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
>>> from apographe.pleiades import Pleiades
>>> p = Pleiades()
>>> p.backend = "web"  # search and fetch pleiades places json over the web
>>> place = p.get("295374")

# data is structured after the Linked Places Format
# https://github.com/LinkedPasts/linked-places-format
>>> place.id
'295374'
>>> place.uri
'https://pleiades.stoa.org/places/295374'
>>> place.names.name_strings
['Zucchabar', 'Ζουχάββαρι', 'Zouchábbari', 'Zouchabbari']
>>> place.properties.asdict()
{'title': 'Zucchabar'}
>>> place.geometry
{"geometries": [{"coordinates": [2.223758, 36.304939], "type": "Point"}, {"coordinates": [2.22619, 36.304782], "type": "Point"}], "type": "GeometryCollection"}
>>> from apographe.linked_places_format import dumps
>>> print(dumps(place, indent=4))
{
    "@context": "https://raw.githubusercontent.com/LinkedPasts/linked-places/master/linkedplaces-context-v1.1.jsonld",
    "type": "FeatureCollection",
    "features": [
        {
            "id_internal": "de2e90ee25ea4dc096c980e916729b33",
            "id": "295374",
            "uri": "https://pleiades.stoa.org/places/295374",
            "properties": {
                "title": "Zucchabar"
            },
            "names": [
                {
                    "romanizations": [
                        "Zucchabar"
                    ]
                },
                {
                    "language_tag": "grc",
                    "romanizations": [
                        "Zouchabbari",
                        "Zouchábbari"
                    ],
                    "toponym": "Ζουχάββαρι"
                }
            ],
            "geometry": {
                "type": "GeometryCollection",
                "geometries": [
                    {
                        "type": "Point",
                        "coordinates": [
                            2.223758,
                            36.304939
                        ]
                    },
                    {
                        "type": "Point",
                        "coordinates": [
                            2.22619,
                            36.304782
                        ]
                    }
                ]
            }
        }
    ]
}

# the raw data as structured and provided by Pleiades is available

>>> from pprint import pformat
>>> raw = pformat(place.raw, indent=4)
>>> print("\n".join(raw.split("\n")[:40]))
{   '@context': {   'created': 'dcterms:created',
                    'dcterms': 'http://purl.org/dc/terms/',
                    'description': 'dcterms:description',
                    'rights': 'dcterms:rights',
                    'snippet': 'dcterms:abstract',
                    'subject': 'dcterms:subject',
                    'title': 'dcterms:title',
                    'uri': '@id'},
    '@type': 'Place',
    'bbox': [2.223758, 36.304782, 2.22619, 36.304939],
    'connections': [   {   '@type': 'Connection',
                           'associationCertainty': 'certain',
                           'attestations': [],
                           'connectionType': 'connection',
                           'connectionTypeURI': 'https://pleiades.stoa.org/vocabularies/relationship-types/connection',
                           'connectsTo': 'https://pleiades.stoa.org/places/285482',
                           'contributors': [],
                           'created': '2016-07-13T13:31:46Z',
                           'creators': [   {   'homepage': None,
                                               'name': '',
                                               'uri': 'https://pleiades.stoa.org/author/admin',
                                               'username': 'admin'}],
                           'description': '',
                           'details': '',
                           'end': None,
                           'history': [],
                           'id': '285482',
                           'provenance': 'Pleiades',
                           'references': [],
                           'review_state': 'published',
                           'start': None,
                           'title': 'Mauretania Caesariensis',
                           'uri': 'https://pleiades.stoa.org/places/295374/285482'}],
    'connectsWith': ['https://pleiades.stoa.org/places/285482'],
    'contributors': [   {'name': 'DARMC', 'username': None},
                        {'name': 'R. Talbert', 'username': None},
                        {   'homepage': None,
                            'name': 'Sean Gillies',
                            'uri': 'https://pleiades.stoa.org/author/sgillies',
                            'username': 'sgillies'},

>>> 
```

# Roadmap

- [x] add search functionality to pleiades web backend
    - [x] title
    - [x] text
    - [x] feature_type
    - [x] tag
    - [x] bbox
    - [ ] author
    - [ ] contributor
    - [ ] provenance
    - [ ] cites
    - [ ] new since
- [ ] add web backends and baseline search for other gazetteers
    - [ ] EDH
    - [x] iDAI
    - [ ] CHGIS
    - [ ] WHG
    - [ ] OpenStreetMap
- [ ] add basic filesystem backend, and then implement pleiades filesystem backend
- [ ] elaborate Place data model mimicking Linked Places Format (mark done when full conformance)
    - [x] id (uri)
    - [x] properties (dict)
        - [x] title (str)
        - [x] *ccodes (list)
    - [ ] ?when (dict)
        - [ ] timespans (list)
            - [ ] +(timespan: dict)
                - [ ] start
                    - [ ] ?in
                    - [ ] ?earliest
                    - [ ] ?latest
                - [ ] ?end
                    - [ ] as for "start", above
        - [ ] ?periods (list)
            - [ ] (period: dict)
                - [ ] name (str)
                - [ ] uri (uri)
        - [ ] ?duration (str)
    - [x] names (list)
        - [x] +(name: dict)  # deviation? Pleiades has unnamed places
            - [x] toponym (str)
            - [x] language_code "lang" (str)
            - [ ] citations (dict)
            - [ ] *when: see further above
    - [ ] ?types (list)
        - [ ] (type: dict)
            - [ ] identifier (str)
            - [ ] label (str)
            - [ ] ?sourceLabels (list)
                - [ ] (source label: dict)
                    - [ ] label (str)
                    - [ ] language code "lang" (str)
            - [ ] ?when
    - [x] geometry (dict): one of geojson.GeometryCollection, Point, etc. or null if no geometry
        - individual geometries can also have (in addition to geojson spec):
            - [ ] ?when
            - [ ] ?certainty (str: certain, less-certain, uncertain)
    - [ ] ?links (list)
        - [ ] (link: dict)
            - [ ] type (str)
            - [ ] identifier (uri)
    - [ ] ?relations (list)
        - [ ] (relation: dict)
            - [ ] relationType (uri)
            - [ ] relationTo (uri)
            - [ ] label (str)
            - [ ] ?when: see further above
            - [ ] citations: see further above
            - [ ] certainty (str)
    - [ ] ?descriptions (list)
        - [ ] (description: dict)
            - [ ] id (uri)
            - [ ] value (str)
            - [ ] language_code "lang" (str)
    - [ ] ?depictions (list)
        - [ ] (depiction: dict)
            - [ ] id (uri)
            - [ ] title (str)
            - [ ] license (uri)
- [ ] extend Place data model to provide lossless recording of Pleiades data
- [ ] create, save, load, export a place collection
    - [ ] create entries by accessioning from search
    - [ ] save (jsonpickle)
    - [ ] load (jsonpickle)
    - [ ] export
        - [x] LPF GEOJSON
            - [ ] option to write multi-part geometries as convex polygons
- [ ] create scripts for various tasks from the commandline

## Search capabilities

Blank cells indicate possible, but not yet implemented, options.

| gazetteer | title | text | feature type | tag | bbox |
| --- | :---: | :---: | :---: | :---: | :---: |
| idai | | yes | | n/a | |
| pleiades | yes | yes | yes | yes | yes |
