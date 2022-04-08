# Apographe

**This python package lets you build and work with a digital gazetteer for small or individual projects.**

- ἀπογραφή: a register or list of lands or property
- gazetteer: a geographic dictionary or index

The "internal gazetteer" can be loaded from and saved to a file in the [Linked Places Format](https://github.com/LinkedPasts/linked-places-format) (LPF: an extension of [GeoJSON](https://datatracker.ietf.org/doc/html/rfc7946)). You can add places to the internal gazetteer by accessioning them from a growing list of external digital gazetteers. *Apographe* enables a common subset of possible queries against the supported gazetteers to facilitate discovery and review.

*Apographe* tries to be polite and speedy. It uses the [webiquette](https://github.com/paregorios/webiquette) package to ensure that all web transactions involved in searching the external gazetteers and retrieving content from them are handled with respect for the `disallow` and `crawl-delay` directives in each external site's robots.txt, with the exception of sites, like *GeoNames*, that host public APIs that bizarrely include a `user-agent * disallow` directive for the API. Moreover, *webiquette* uses the [requests-cache](https://github.com/reclosedev/requests-cache) package to ensure that web transactions are locally cached according to rules found in the response headers supplied by the individual sites (or sensible defaults) so that subsequent lookups draw from the local cache instead of hitting the website over and over.

*Apographe* is written and maintained by [Tom Elliott](https://isaw.nyu.edu/people/staff/tom-elliott) for the [Institute for the Study of the Ancient World](https://isaw.nyu.edu).  
Copyright 2022 New York University.  
This software is published and distributed under the terms of the *GNU Affero General Public License,* version 3 (see LICENSE.txt for details).

## Installation

*Apographe* needs a python 3.10.2 or greater virtual environment. 

Activate the virtual environment and then:

```
pip install -U git+https://github.com/isawnyu/apographe.git
```

Then you can either work on the command line or in code.

## Getting started (command line)

Start the command-line interface:

```
$ python scripts/cli.py 
    _                                      _          
   / \   _ __   ___   __ _ _ __ __ _ _ __ | |__   ___ 
  / _ \ | '_ \ / _ \ / _` | '__/ _` | '_ \| '_ \ / _ \
 / ___ \| |_) | (_) | (_| | | | (_| | |_) | | | |  __/
/_/   \_\ .__/ \___/ \__, |_|  \__,_| .__/|_| |_|\___|
        |_|          |___/          |_|               

Supported gazetteers                                                
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ name     ┃ description                                           ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ idai     │ iDAI Gazetteer of the German Archaeological Institute │
│ pleiades │ Pleiades gazetteer of ancient places                  │
└──────────┴───────────────────────────────────────────────────────┘
type 'help' for a list of commands
> help
Supported commands                                                                        
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Command    ┃ Description                                                               ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ accession  │ Collect a place from a gazetteer and convert/copy it to the internal      │
│            │ gazetteer.                                                                │
│ align      │ Attempt to align one or more items in the internal gazetteer with items   │
│            │ in an external gazetteer.                                                 │
│ change     │ Change the value of a field of a place in the internal gazetteer          │
│ full       │ Show full information about a place in the internal gazetteer.            │
│ gazetteers │ List supported gazetteers.                                                │
│ help       │ List available commands or get help with using an individual command.     │
│ import     │ Import a file for subsequent use.                                         │
│ imports    │ List contents of imported data.                                           │
│ internal   │ List all places in the internal gazetteer.                                │
│ load       │ Load LPF JSON files on the local filesystem into the internal gazetteer.  │
│ quit       │ Quit the program.                                                         │
│ save       │ Save the contents of the internal gazetteer to the local filesystem.      │
│ search     │ Search a gazetteer.                                                       │
└────────────┴───────────────────────────────────────────────────────────────────────────┘
> search pleiades zucchabar
Pleiades search results                                                                   
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID     ┃ Summary                                                                       ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 295374 │ Zucchabar                                                                     │
│        │ https://pleiades.stoa.org/places/295374                                       │
│        │ Zucchabar was an ancient city of Mauretania Caesariensis with Punic origins.  │
│        │ The modern Algerian community of Miliana lies atop and around the largely     │
│        │ unexcavated ancient site. Epigraphic evidence indicates that the Roman        │
│        │ emperor Augustus established a veteran colony there.                          │
└────────┴───────────────────────────────────────────────────────────────────────────────┘
> accession pleiades 295374
Accessioned place                                            
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ place key       ┃ place                                   ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ pleiades:295374 │ Zucchabar                               │
│                 │ https://pleiades.stoa.org/places/295374 │
│                 │ NotImplemented                          │
└─────────────────┴─────────────────────────────────────────┘
> import ~/scratch/pids.txt
Imported txt file /Users/paregorios/scratch/pids.txt and stored data as imports:pids.
> imports
pids
> imports pids
[
    '216744',
    '217016',
    '220489',
    '229670928',
    '266004',
    '297163719',
    '412998',
    '413010',
    '413025',
    '413103',
    '413133',
    '413383',
    '422843',
    '423060',
    '438775',
    '580782181',
    '599664',
    '668331',
    '678160',
    '711164401',
    '776189',
    '830595307',
    '912803',
    '912841',
    '912851'
]
> accession pleiades imports:pids
Accessioned place                                                                                             
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ place key                                ┃ place                                                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ callatis                                 │ Callatis                                                        │
│                                          │ https://pleiades.stoa.org/places/216744                         │
│                                          │ A Greek colony and port on the west coast of the Black Sea,     │
│                                          │ modern Mangalia in Romania.                                     │
│ tomis                                    │ Tomis                                                           │
│                                          │ https://pleiades.stoa.org/places/217016                         │
│                                          │ Tomis was founded as a Greek colony on the Black Sea coast ca.  │
│                                          │ 600 B.C.                                                        │
│ unnamed-road-sequence-deultum-to-argamum │ Unnamed road sequence: Deultum to Argamum                       │
│                                          │ https://pleiades.stoa.org/places/220489                         │
│                                          │ Deultum → Anchialus → Odessus → Dionysopolis → Tirizis →        │
│                                          │ Callatis → Tomis → Histria → Argamum → E                        │
│ via-ciminia                              │ Via Ciminia                                                     │
│                                          │ https://pleiades.stoa.org/places/229670928                      │
│                                          │ The Via Ciminia was a Roman road that left the Via Cassia and   │
│                                          │ continued toward the Ciminian hills. Its course likely ran from │
│                                          │ Sutrium to near Viterbo.                                        │
│ pollentia                                │ Pollentia                                                       │
│                                          │ https://pleiades.stoa.org/places/266004                         │
│                                          │ An ancient place, cited: BAtlas 27 inset Pollentia              │
│ temple-of-mater-matuta-at-satricum       │ Temple of Mater Matuta at Satricum                              │
│                                          │ https://pleiades.stoa.org/places/297163719                      │
│                                          │ A sanctuary dedicated to Mater Matuta that was in use between   │
│                                          │ the seventh and fifth centuries B.C.                            │
│ ad-vicesimum                             │ Ad Vicesimum                                                    │
│                                          │ https://pleiades.stoa.org/places/412998                         │
│                                          │ An ancient place, cited: BAtlas 42 C4 Ad Vicesimum              │
│ alsietinus-lacus                         │ Alsietinus lacus                                                │
│                                          │ https://pleiades.stoa.org/places/413010                         │
│                                          │ The Alsietinus lacus, modern Lago di Martignano, is a small     │
│                                          │ volcanic crater-lake in southern Etruria. The lake was the      │
│                                          │ source of the Augustan aqueduct aqua Augusta Alsietina that     │
│                                          │ served non-potable water to the Transtiberim and Ianiculum.     │
│ aquae-passeris                           │ Aquae Passeris                                                  │
│                                          │ https://pleiades.stoa.org/places/413025                         │
│                                          │ An ancient place, cited: BAtlas 42 C4 Aquae Passeris            │
│ corchiano                                │ Corchiano                                                       │
│                                          │ https://pleiades.stoa.org/places/413103                         │
│                                          │ Corchiano was the site of a wealthy settlement in the Ager      │
│                                          │ Faliscus that was in proximity to the Via Amerina.              │
│ fescennium                               │ Fescennium                                                      │
│                                          │ https://pleiades.stoa.org/places/413133                         │
│                                          │ Fescennium (modern Narce) was a Faliscan settlement located ca. │
│                                          │ 5 km south of Falerii Veteres.                                  │
│ vignanello                               │ Vignanello                                                      │
│                                          │ https://pleiades.stoa.org/places/413383                         │
│                                          │ An ancient place, cited: BAtlas 42 C4 Vignanello                │
│ ardea                                    │ Ardea                                                           │
│                                          │ https://pleiades.stoa.org/places/422843                         │
│                                          │ Ardea was an ancient settlement of the Rutuli in Latium.        │
│ satricum                                 │ Satricum                                                        │
│                                          │ https://pleiades.stoa.org/places/423060                         │
│                                          │ An ancient settlement on the right bank of the river Astura,    │
│                                          │ Satricum has a mixed heritage of Latins and Volscians. In 499   │
│                                          │ B.C. Satricum was a member of the Latin League, but was under   │
│                                          │ Volscian control in 488 B.C. The site is noted for its          │
│                                          │ sanctuary of Mater Matuta.                                      │
│ longula                                  │ Longula                                                         │
│                                          │ https://pleiades.stoa.org/places/438775                         │
│                                          │ Longula was an early settlement of Latium Vetus, although its   │
│                                          │ location is no longer known. A Volscian city, Longula was first │
│                                          │ taken by the Romans in 493 B.C. under the consul Postumus       │
│                                          │ Cominius. It subsequently changes hands several times during    │
│                                          │ the fifth and fourth centuries B.C. It likely lay between Ardea │
│                                          │ and Antium.                                                     │
│ villa-romana-balaca                      │ Villa Romana Baláca                                             │
│                                          │ https://pleiades.stoa.org/places/580782181                      │
│                                          │ The site of a Roman villa that was discovered in 1904 in the    │
│                                          │ Balácapuszta field of Vámos village in western Hungary.         │
│ iasos                                    │ Iasos                                                           │
│                                          │ https://pleiades.stoa.org/places/599664                         │
│                                          │ Iasos was an ancient Greek city in Caria.                       │
│ palmyra                                  │ Palmyra                                                         │
│                                          │ https://pleiades.stoa.org/places/668331                         │
│                                          │ An ancient oasis and trading city with monumental remains,      │
│                                          │ located in modern Syria. Under Zenobia, Palmyra was the capital │
│                                          │ of the breakaway Palmyrene Empire, leading to Aurelian's razing │
│                                          │ of the city. Inscribed as a UNESCO World Heritage Site in 1980. │
│ gerra                                    │ Gerra                                                           │
│                                          │ https://pleiades.stoa.org/places/678160                         │
│                                          │ Gerra (modern Anjar, Lebanon) was a stronghold built under the  │
│                                          │ Umayyad Caliph Al-Walid ibn Abdel Malek in the eighth century   │
│                                          │ AD. It was listed as a UNESCO World Heritage Site in 1984.      │
│ tomb-of-the-ottavii                      │ Tomb of the Ottavii                                             │
│                                          │ https://pleiades.stoa.org/places/711164401                      │
│                                          │ A mid-third century AD hypogeum tomb.                           │
│ kellis                                   │ Kellis                                                          │
│                                          │ https://pleiades.stoa.org/places/776189                         │
│                                          │ Roman/late antique settlement, with substantial remains of      │
│                                          │ public religious buildings, including a large temple,           │
│                                          │ residential areas, tombs, and three churches.                   │
│ gallese                                  │ Gallese                                                         │
│                                          │ https://pleiades.stoa.org/places/830595307                      │
│                                          │ Gallese is a settlement located about 14 km north of Civita     │
│                                          │ Castellana. It was active especially in Faliscan times and      │
│                                          │ again during late antiquity and the middle ages.                │
│ al-qusur                                 │ al-Qusur                                                        │
│                                          │ https://pleiades.stoa.org/places/912803                         │
│                                          │ An ancient place, cited: BAtlas 93 E4 al-Qusur                  │
│ e-kara-icarus-island                     │ E-kara/Icarus (island)                                          │
│                                          │ https://pleiades.stoa.org/places/912841                         │
│                                          │ Failaka Island in the Persian Gulf.                             │
│ failaka-tell-khazne                      │ Failaka/Tell Khazne                                             │
│                                          │ https://pleiades.stoa.org/places/912851                         │
│                                          │ An ancient place, cited: BAtlas 93 E4 Failaka/Tell Khazne       │
└──────────────────────────────────────────┴─────────────────────────────────────────────────────────────────┘
> align pleiades gallese
alignment results                                                                                             
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Internal ID ┃ Gazetteer ID ┃ Summary                                                                       ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ gallese     │ 830595307    │ Gallese                                                                       │
│             │              │ https://pleiades.stoa.org/places/830595307                                    │
│             │              │ Gallese is a settlement located about 14 km north of Civita Castellana. It    │
│             │              │ was active especially in Faliscan times and again during late antiquity and   │
│             │              │ the middle ages.                                                              │
└─────────────┴──────────────┴───────────────────────────────────────────────────────────────────────────────┘
>
```


## Getting started (code)

You can do stuff like:

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

See now the github issue tracker at: https://github.com/isawnyu/apographe/issues
