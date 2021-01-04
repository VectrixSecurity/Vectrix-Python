from tests import MetadataElement, MetadataPriority

correct_metadata = {
    "value_link": {
        "priority": -1,
        "value": "sample metadata with link in value and link https://localhost.com",
        "link": "https://localhost.com:8000"
    },
    "value": {
        "priority": 0,
        "value": "sample metadata with link in value https://localhost.com",
        "link": "https://localhost.com"
    },
    "no_link": {
        "priority": 50,
        "value": "sample metadata without link"
    },
    "link": {
        "priority": 100,
        "value": "sample metadata with link in link",
        "link": "https://localhost.com:8000"
    },
    "custom_priority": {
        "priority": 23,
        "value": "custom priority"
    }
}


def test_metadata_link_value_link():
    test_metadata = MetadataElement(MetadataPriority.DO_NOT_SURFACE,
                                    "sample metadata with link in value and link https://localhost.com", "https://localhost.com:8000").to_dict()

    assert test_metadata == correct_metadata['value_link']


def test_metadata_value_link():
    test_metadata = MetadataElement(MetadataPriority.LOW, "sample metadata with link in value https://localhost.com").to_dict()

    assert test_metadata == correct_metadata['value']


def test_metadata_no_link():
    test_metadata = MetadataElement(MetadataPriority.MEDIUM, "sample metadata without link").to_dict()

    assert test_metadata == correct_metadata['no_link']


def test_metadata_link_link():
    test_metadata = MetadataElement(MetadataPriority.HIGH, "sample metadata with link in link", "https://localhost.com:8000").to_dict()

    assert test_metadata == correct_metadata['link']


def test_metadata_custom_priority():
    test_metadata = MetadataElement(23, 'custom priority').to_dict()

    assert test_metadata == correct_metadata['custom_priority']
