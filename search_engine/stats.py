import numpy as np
from utils.redis import redis
from utils.redis.keys import SearchEngine as SEK


def get_document_frequency_pairs_for_term(collection_kind, term):
    '''
    Returns a list of document-frequency pairs (first element of
    a pair contains the document ID and the second contains the
    frequency of the term in said document).
    '''
    collection = SEK.fdt_name(collection_kind, term)
    pairs = redis.zrange(collection, 0, -1, desc=True, withscores=True)
    return [(int(doc_ID), int(freq)) for (doc_ID, freq) in pairs]


def get_frequency_of_term_in_document(collection_kind, term, doc_ID):
    '''
    Gets the frequency of the given term in the given document.
    '''
    collection = SEK.fdt_name(collection_kind, term)
    return int(redis.zscore(collection, doc_ID))


def get_number_of_terms(collection_kind):
    '''
    Get the total number of terms in the given collection.
    '''
    frequencies = 0
    for v in redis.hvals(SEK.ft_name(collection_kind)):
        frequencies += int(v)

    return frequencies


def get_number_of_documents(collection_kind):
    '''
    Get the total number of documents in the given collection.
    '''
    return len(redis.hkeys(SEK.wd_name(collection_kind)))


def get_number_of_documents_containing_term(collection_kind, term):
    collection = SEK.fdt_name(collection_kind, term)
    return len(redis.zrange(collection, 0, -1))


def get_magnitude_of_weights_vector(collection_kind, doc_ID):
    return float(redis.hmget(SEK.wd_name(collection_kind), doc_ID)[0])


def get_weight_of_term_in_document(term_frequency_in_document):
    if term_frequency_in_document:
        return 1 + np.log(term_frequency_in_document)
    else:
        return 0


def get_weight_of_term_in_query(collection_kind, term):
    N = get_number_of_terms(collection_kind)
    ft = get_number_of_documents_containing_term(collection_kind, term)
    if ft:
        return np.log(1 + N/ft)
    else:
        return 0


def get_magnitude_of_vector(vector):
    '''
    Vector is a list of quantities.

    Returns the square root of the sum of the squares
    of the terms.
    '''
    v = np.array(vector)
    return np.sqrt(v.dot(v))
