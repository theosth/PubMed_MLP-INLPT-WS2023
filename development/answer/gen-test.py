
from langchain_core.documents import Document

from answer_generation import GenAI

test_docs = [
    Document(page_content="Jesse loves red but not yellow"),
    Document(page_content = "Jamal loves green but not as much as he loves orange"),
    Document(page_content = "Jesse's favorite color is red"),
]

pubmed_test_docs = [
    Document(page_content="recent advances in artificial intelligence technology have significantly improved facial image manipulation, which is known as deepfake. facial image manipulation synthesizes or replaces a region of the face in an image with that of another face. the techniques for facial image manipulation are classified into four categories : ( 1 ) entire face synthesis, ( 2 ) identity swap, ( 3 ) attribute manipulation, and ( 4 ) expression swap. out of them, we focus on expression swap because it effectively manipulates only the expression of the face in the images or videos without creating or replacing the entire face, having advantages for the real - time application. in this study, we propose an evaluation framework of the expression swap models targeting the real - time online class environments. for this, we define three kinds of scenarios according to the portion of the face in the entire image considering actual online class situations : ( 1 ) attendance check ( scenario 1 ), ( 2 ) presentation ( scenario 2 ), and ( 3 ) examination ( scenario 3 ). considering the manipulation on the online class environments, the framework receives a single source image and a target video and generates the video that manipulates a face of the target video to that in the source image. to this end, we select two models that satisfy the",),
]

pubmed_test_docs1 = [
    Document(page_content="artificial intelligence ( ai ) systems utilizing deep neural networks and machine learning ( ml ) algorithms are widely used for solving critical problems in bioinformatics, biomedical informatics and precision medicine. however, complex ml models that are often perceived as opaque and black - box methods make it difficult to understand the reasoning behind their decisions. this lack of transparency can be a challenge for both end - users and decision - makers, as well as ai developers. in sensitive areas such as healthcare, explainability and accountability are not only desirable properties but also legally required for ai systems that can have a significant impact on human lives. fairness is another growing concern, as algorithmic decisions should not show bias or discrimination towards certain groups or individuals based on sensitive attributes. explainable ai ( xai ) aims to overcome the opaqueness of black - box models and to provide transparency in how ai systems make decisions. interpretable ml models can explain how they make predictions and identify factors that influence their outcomes. however, the majority of the state - of - the - art interpretable ml methods are domain - agnostic and have evolved from fields such as computer vision, automated reasoning or statistics, making direct application to bioinformatics problems challenging without customization and domain adaptation. in this paper, we discuss the importance of explainability and algorithm"),
]

pubmed_test_docs2 = [
    Document(page_content="""performance of all the algorithms was compared with the experts'performance. to better understand the algorithms and clarify the direction of optimization, misclassification and visualization heatmap analyses were performed. < b > results : < / b > in five - fold cross - validation, algorithm i achieved robust performance, with accuracy = 97. 36 % ( 95 % ci : 0. 9697, 0. 9775 ), auc = 0. 995 ( 95 % ci : 0. 9933, 0. 9967 ), sensitivity = 93. 92 % ( 95 % ci : 0. 9333, 0. 9451 ), and specificity = 98. 19 % ( 95 % ci : 0. 9787, 0. 9852 ). the macro - auc, accuracy, and quadratic - weighted kappa were 0. 979, 96. 74 % ( 95 % ci : 0. 963, 0. 9718 ), and 0. 988 ( 95 % ci : 0. 986, 0. 990 ) for algorithm ii. algorithm iii achieved an accuracy of 0. 9703 to 0. 9941 for classifying the " plus " lesions and an f1 - score of 0. 6855 to 0. 8890 for detecting and localizing lesions. the performance metrics in external"""),
]

chain = GenAI()

print(chain.invoke(test_docs, "Is Jesse's favorite color orange?"))
print(chain.invoke(test_docs, "What is Theo's favorite color?"))
print(chain.invoke(test_docs, "Are penguins birds?"))

print(chain.invoke(pubmed_test_docs, "What are the four categories of facial image manipulation techniques?"))

print(chain.invoke(pubmed_test_docs1, "Are AI systems utilizing deep neural networks and machine learning algorithms widely used for solving critical problems in bioinformatics, biomedical informatics, and precision medicine?"))

print(chain.invoke(pubmed_test_docs2, "What is the accuracy of algorithm i in five-fold cross-validation?"))

