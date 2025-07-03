## Tests for Fora AI v2

Features should have their own folder for tests
```
tests/
├── __init__.py 
├── feature_1/
│   ├── __init__.py                  
│   ├── test_1.py
│   ├── test_2.py
│   └── test_3.py
├── feature_2/
│   ├── __init__.py                  
│   ├── test_1.py
│   ├── test_2.py
│   └── test_3.py
├── conftest.py      # Common configuration                    
└── README.md                           
```

### File name
Each file name should say what is being tests<br>
1. `test_summaries_generation.py` -> this is testing the generation functions for summaries
2. `test_summaries_helpers.py`    -> this is testing the helper functions for summaries

### Function name
The function names should follow this pattern:<br>
`def test__{function being tests}__{what is being tested/output of test}:`<br>
For example: `def test__write_summary_ai__success:`

### LOGFIRE
MAKE SURE LOGFIRE IS MOCKED<br>
To ensure unnecessary use of logfire, make sure to mock it<br>
To do so add this following line to `mock_` or `setup_method` function of setup function:<br>
`logfire.configure(send_to_logfire = False)`