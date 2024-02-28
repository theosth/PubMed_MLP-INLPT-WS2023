from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
import opensearch_connector as oc
from retrieval_wrapper import Document
import numpy as np

def get_confidence_category(query: str, documents: list[Document]) -> list[str]:
    abstract_embeddings = oc.MODEL.encode([doc.abstract for doc in documents])
    query_embedding = oc.MODEL.encode(query)
    sim = cosine_similarity(query_embedding, abstract_embeddings)
    categories = []
    # empirically chosen thresholds
    for score in sim:
        if score > 0.85:
            categories.append('high')
        elif score > 0.8:
            categories.append('medium')
        else:
            categories.append('low')
    return categories


def cosine_similarity(v1, vectors):
    dot_product = np.dot(vectors, v1)
    
    norm_v1 = np.linalg.norm(v1)
    norms_vectors = np.linalg.norm(vectors, axis=1)
    
    similarity = dot_product / (norm_v1 * norms_vectors)
    
    return similarity


if __name__ == "__main__":
    res = get_confidence_category("What are the problems of deaf children in school?", [
        Document(pmid="1", title="title", abstract="the purpose of this study was to examine several behavioral problems in school - aged hearing - impaired children with hearing aids or cochlear implants, compared to normally hearing children. additionally, we wanted to investigate which sociodemographic, linguistic, and medical factors contributed to the level of behavioral problems, to pinpoint where targeted interventions can take place. this large, retrospective study included a sample of 261 school - aged children ( mean age = 11. 8 years, sd = 1. 6 ), that consisted of three age - and gender - matched subgroups : 75 with hearing aids, 57 with cochlear implants, and 129 normally hearing controls. self - and parent - reports concerning reactive and proactive aggression, delinquency, and symptoms of psychopathy, attention deficit hyperactivity disorder, oppositional defiant disorder, and conduct disorder were used. in addition, several language and intelligence tests were administered. hearing - impaired children showed significantly more proactive aggression, symptoms of psychopathy, attention deficit hyperactivity disorder, oppositional defiant disorder, and conduct disorder than their normally hearing peers. more behavioral problems were associated with special schools for the deaf, sign ( - supported ) language, hearing aids ( in contrast to cochlear implants ), higher age, male gender, lower socioeconomic status, lower intelligence, and delayed language development. hearing", author_list=["author"], doi="doi", keyword_list=["keyword"]),
        Document(pmid="1", title="title", abstract="lexical gap in cqa search, resulted by the variability of languages, has been recognized as an important and widespread phenomenon. to address the problem, this paper presents a question reformulation scheme to enhance the question retrieval model by fully exploring the intelligence of paraphrase in phrase - level. it compensates for the existing paraphrasing research in a suitable granularity, which either falls into fine - grained lexical - level or coarse - grained sentence - level. given a question in natural language, our scheme first detects the involved key - phrases by jointly integrating the corpus - dependent knowledge and question - aware cues. next, it automatically extracts the paraphrases for each identified key - phrase utilizing multiple online translation engines, and then selects the most relevant reformulations from a large group of question rewrites, which is formed by full permutation and combination of the generated paraphrases. extensive evaluations on a real world data set demonstrate that our model is able to characterize the complex questions and achieves promising performance as compared to the state - of - the - art methods.", author_list=["author"], doi="doi", keyword_list=["keyword"])
        ])
    print(res)