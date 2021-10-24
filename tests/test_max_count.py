import pytest
import spacy

from replacy import ReplaceMatcher

nlp = spacy.load("en_core_web_sm")

# They read us the stories they themselves had written.

match_dict = {
    "match-1": {
        "patterns": [[
            {"LOWER": {"IN": ["they", "she"]}},
            {"LEMMA": "read", "TEMPLATE_ID": 1},
            {"LOWER": "us"},
            {"LOWER": "the"},
            {"LEMMA": "story", "TEMPLATE_ID": 1},
            {"LOWER": {"IN": ["they", "she"]}},
            {"LOWER": {"IN": ["themselves", "herself"]}},
            {"LEMMA": "have", "OP": "*"},
            {"LEMMA": {"IN": ["write", "made"]}},
        ]],
        "suggestions": [
            [
                {"PATTERN_REF": 0},
                {"TEXT": {"IN": ["sing", "give"]}, "FROM_TEMPLATE_ID": 1},
                {"PATTERN_REF": 2},
                {"TEXT": {"IN": ["a", "the", "some"]}},
                {"TEXT": "story", "INFLECTION": "NOUN"},
                {"PATTERN_REF": 5, "REPLACY_OP": "UPPER"},
                {"PATTERN_REF": 6},
                {"TEXT": {"IN": ["write", "made", "create"]}, "INFLECTION": "VBD"},
            ]
        ],
        "test": {"positive": [], "negative": []},
    }
}

outputs = [
    "They sang us a stories THEY themselves wrote",
    "They sang us a stories THEY themselves made",
    "They sang us a stories THEY themselves created",
    "They gave us a stories THEY themselves wrote",
    "They gave us a stories THEY themselves made",
    "They gave us a stories THEY themselves created",
    "They sang us the story THEY themselves wrote",
    "They sang us the story THEY themselves made",
    "They sang us the story THEY themselves created",
    "They gave us the story THEY themselves wrote",
    "They gave us the story THEY themselves made",
    "They gave us the story THEY themselves created",
]

output_default_max_count_1 = [
    "They sang us a stories THEY themselves wrote",
    "They sang us a story THEY themselves made",
    "They gave us a stories THEY themselves made",
    "They gave us a story THEY themselves wrote",
    "They sang us the stories THEY themselves made",
    "They sang us the story THEY themselves wrote",
    "They gave us the stories THEY themselves wrote",
    "They gave us the story THEY themselves made",
    "They sang us some stories THEY themselves created",
    "They gave us some story THEY themselves created",
]

r_matcher1 = ReplaceMatcher(
    nlp,
    match_dict=match_dict,
    lm_path="./replacy/resources/test.arpa",
    filter_suggestions=True,
)

spans = r_matcher1("They read us the stories they themselves had written.")
suggestions = spans[0]._.suggestions


def test_suggestions():
    assert suggestions == outputs


r_matcher_max_count_1 = ReplaceMatcher(
    nlp,
    match_dict=match_dict,
    lm_path="./replacy/resources/test.arpa",
    filter_suggestions=True,
    default_max_count=1,
)

spans_max_count_1 = r_matcher_max_count_1(
    "They read us the stories they themselves had written."
)
suggestions_max_count_1 = spans_max_count_1[0]._.suggestions


def test_default_max_count():
    assert suggestions_max_count_1 == output_default_max_count_1


short_match_dict_2_sugg = {
    "match-1": {
        "patterns": [[
            {"LOWER": {"IN": ["they", "she"]}},
            {"LEMMA": "read", "TEMPLATE_ID": 1},
        ]],
        "suggestions": [
            [
                {"PATTERN_REF": 0},
                {"FROM_TEMPLATE_ID": 1, "TEXT": {"IN": ["sing", "give"]}},
            ],
            [{"PATTERN_REF": 0}, {"FROM_TEMPLATE_ID": 1, "TEXT": "dance"},],
        ],
        "test": {"negative": [], "positive": []},
    }
}


def test_multiple_suggestions_max_count():
    r_matcher = ReplaceMatcher(
        nlp,
        match_dict=short_match_dict_2_sugg,
        lm_path="./replacy/resources/test.arpa",
        filter_suggestions=True,
        debug=True,
    )
    spans = r_matcher("They read us the stories they themselves had written.")
    assert len(spans[0]._.suggestions) == 3


short_match_dict = {
    "match-1": {
        "patterns": [[
            {"LOWER": {"IN": ["they", "she"]}},
            {"LEMMA": "read", "TEMPLATE_ID": 1},
        ]],
        "suggestions": [
            [
                {"PATTERN_REF": 0},
                {"FROM_TEMPLATE_ID": 1, "TEXT": {"IN": ["sing", "give"]}},
            ]
        ],
        "test": {"negative": [], "positive": []},
    }
}


def test_manual_max_count():
    # use short match dict
    # default_max_count=1
    # expect 1 suggestion

    r_matcher = ReplaceMatcher(
        nlp,
        match_dict=short_match_dict,
        lm_path="./replacy/resources/test.arpa",
        filter_suggestions=True,
        default_max_count=1,
        debug=True,
    )
    spans = r_matcher("They read us the stories they themselves had written.")
    assert len(spans[0]._.suggestions) == 1

    # MAX_COUNT=2 for ['sing', 'give']
    # default_max_count=1
    # expect 2 suggestions

    short_match_dict["match-1"]["suggestions"][0][1]["MAX_COUNT"] = 2

    r_matcher = ReplaceMatcher(
        nlp,
        match_dict=short_match_dict,
        lm_path="./replacy/resources/test.arpa",
        filter_suggestions=True,
        default_max_count=1,
        debug=True,
    )
    spans = r_matcher("They read us the stories they themselves had written.")
    suggestions = spans[0]._.suggestions

    assert len(spans[0]._.suggestions) == 2
