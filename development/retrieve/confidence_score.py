import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import development.retrieve.opensearch_connector as oc
from development.retrieve.retrieval_wrapper import Document


WORST_CONFIDENCE_COS_SIM = 80
PERFECT_CONFIDENCE_COS_SIM = 100
CONFIDENCE_SCALING_FACTOR = 1.5


def compute_confidence_ratings(query: str, texts: list[str]) -> list[int]:
    """
    This function calculates the confidence rating of a query to a list of texts with cosine similarity.

    :param query: The query string.
    :param texts: A list of texts objects.
    :return: A list of confidence categories corresponding to each text.
    """
    if len(texts) == 0:
        return []
    
    # Compute Embeddings
    abstract_embeddings = oc.MODEL.encode(texts)
    query_embedding = oc.MODEL.encode(query)

    # Compute Distance
    cosine_sim = cosine_similarity(query_embedding, abstract_embeddings)
    perc_dist = (np.pi - np.arccos(cosine_sim)) * 100 / np.pi

    # Compute Confidence
    # -------------------------------------------------------------------
    # Note: We have noted that even (intentionally) bad matches lead to
    # high cosine similarity values. However, they are always in the
    # range of [0.8:1.0] for bad to perfect matches. Those values have
    # been determined empirically.
    #
    # Thus, we subtract the worst possible similarity. Then, we multiply
    # it by some factor > 1, so that larger scores are rewarded (scaled
    # more) and then those values are scaled into a range of [0.0:1.0].
    # -------------------------------------------------------------------
    confidence = np.maximum(0.0, perc_dist - WORST_CONFIDENCE_COS_SIM)
    confidence = confidence * CONFIDENCE_SCALING_FACTOR
    range_scale_factor = (PERFECT_CONFIDENCE_COS_SIM / (PERFECT_CONFIDENCE_COS_SIM - WORST_CONFIDENCE_COS_SIM))
    confidence = np.minimum(PERFECT_CONFIDENCE_COS_SIM, confidence * range_scale_factor)
    return [int(x) for x in confidence]


def cosine_similarity(v1, vectors):
    """
    Calculates the cosine similarity between v1 and each vector in vectors.

    :param v1: The first vector.
    :param vectors: The list of vectors.
    :return: cosine similarities.
    """
    dot_product = np.dot(vectors, v1)
    norm_v1 = np.linalg.norm(v1)
    norms_vectors = np.linalg.norm(vectors, axis=1)
    similarity = dot_product / (norm_v1 * norms_vectors)
    return similarity


#############################
#       Example Usage       #
#############################
if __name__ == "__main__":
    res = compute_confidence_ratings(
        "What are the problems of deaf children in school?",
        [
            Document(
                pmid="1",
                title="title",
                abstract="the purpose of this study was to examine several behavioral problems in school - aged hearing - impaired children with hearing aids or cochlear implants, compared to normally hearing children. additionally, we wanted to investigate which sociodemographic, linguistic, and medical factors contributed to the level of behavioral problems, to pinpoint where targeted interventions can take place. this large, retrospective study included a sample of 261 school - aged children ( mean age = 11. 8 years, sd = 1. 6 ), that consisted of three age - and gender - matched subgroups : 75 with hearing aids, 57 with cochlear implants, and 129 normally hearing controls. self - and parent - reports concerning reactive and proactive aggression, delinquency, and symptoms of psychopathy, attention deficit hyperactivity disorder, oppositional defiant disorder, and conduct disorder were used. in addition, several language and intelligence tests were administered. hearing - impaired children showed significantly more proactive aggression, symptoms of psychopathy, attention deficit hyperactivity disorder, oppositional defiant disorder, and conduct disorder than their normally hearing peers. more behavioral problems were associated with special schools for the deaf, sign ( - supported ) language, hearing aids ( in contrast to cochlear implants ), higher age, male gender, lower socioeconomic status, lower intelligence, and delayed language development. hearing",
                author_list=["author"],
                doi="doi",
                keyword_list=["keyword"],
            ),
            Document(
                pmid="1",
                title="title",
                abstract="lexical gap in cqa search, resulted by the variability of languages, has been recognized as an important and widespread phenomenon. to address the problem, this paper presents a question reformulation scheme to enhance the question retrieval model by fully exploring the intelligence of paraphrase in phrase - level. it compensates for the existing paraphrasing research in a suitable granularity, which either falls into fine - grained lexical - level or coarse - grained sentence - level. given a question in natural language, our scheme first detects the involved key - phrases by jointly integrating the corpus - dependent knowledge and question - aware cues. next, it automatically extracts the paraphrases for each identified key - phrase utilizing multiple online translation engines, and then selects the most relevant reformulations from a large group of question rewrites, which is formed by full permutation and combination of the generated paraphrases. extensive evaluations on a real world data set demonstrate that our model is able to characterize the complex questions and achieves promising performance as compared to the state - of - the - art methods.",
                author_list=["author"],
                doi="doi",
                keyword_list=["keyword"],
            ),
        ],
    )
    print(res)
