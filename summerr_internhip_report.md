


SIKKIM MANIPAL INSTITUTE OF TECHNOLOGY
(A Constituent Institute of Sikkim Manipal University)
Majitar, Sikkim – 737136

Summer Internship Report
On
Menu Automation System
A report submitted in partial fulfillment of the requirements 
For the Summer Internship Program

SUBMITTED BY:
Aditya Prasad (Reg No: 202400333)
Department of AI&DS
Sikkim Manipal Institute of Technology, SMU

Supervised By:
Ankit Chhetri
Technical Head,
EMEYC Pvt. Ltd

ABSTRACT

Restaurant menu digitization and standardization are important for improving operational efficiency, reducing manual effort, and enabling seamless integration with digital ordering platforms. This internship project presents an AI-powered Menu Automation System that automates the extraction and structuring of menu information from restaurant menus using Optical Character Recognition (OCR) and Large Language Models (LLMs). The system processes menu images and PDF documents, extracts textual content, corrects OCR inaccuracies, identifies menu categories and food items, and generates a clean, standardized JSON representation suitable for downstream applications. The pipeline incorporates document preprocessing, AI-based information extraction, metadata generation, and structured data validation to improve the quality and consistency of the generated output. The developed solution significantly reduces the time required for manual menu creation while maintaining high data quality and flexibility across different menu layouts. Experimental evaluation on a diverse collection of restaurant menus demonstrated that the system is capable of accurately extracting and organizing menu information from varying document formats, making it a practical solution for restaurant digitization and intelligent food service applications. Future work may focus on improving multilingual support, handwritten menu recognition, and real-time menu updating capabilities.

TABLE OF CONTENTS
Section	Page
Abstract 	2
Introduction	4
Motivation and Problem Statement	5
Objectives and Tech Stack 	6
Methodology 	8
Implementation and Work Done	9
Training Process and Evidence	10
Results and Discussion	11
Error Analysis 	12
Comparison with existing work	13
Limitations and challenges 	14
Future Scope	15
Conclusion and References	16








PROJECT AT A GLANCE
Item	Verified detail
Project title	Menu Automation System
AI model	Google Gemini 2.5 Flash
Final Perfomance	Successfully extracts menu categories, food items, descriptions, prices, and also finds the best quality copyright free images for diverse restaurant menus with high consistency and significantly reduces manual data entry


INTRODUCTION

Restaurant menus are essential for presenting food offerings to customers, but manually digitizing and maintaining menu information is often a time-consuming, error-prone, and repetitive process. Restaurants and food delivery platforms frequently receive menus in various formats, such as scanned documents, images, and PDF files, which require significant manual effort to extract, organize, and standardize into structured digital data. This process can lead to inconsistencies, increased operational costs, and delays in updating menu information across digital platforms.
Recent advancements in Optical Character Recognition (OCR), Natural Language Processing (NLP), and Large Language Models (LLMs) have significantly improved the automation of document understanding and information extraction tasks. Modern AI systems can accurately extract textual content from complex menu layouts, correct OCR errors, identify menu categories, food items, descriptions, and prices, and convert unstructured documents into structured machine-readable formats. These technologies enable faster, more accurate, and scalable menu digitization compared to traditional manual methods.
The internship involved studying AI-based document processing techniques and developing a Menu Automation System capable of automatically extracting and organizing menu information from restaurant menu documents. The implemented system integrates OCR for text extraction, AI-powered language models for information correction and structuring, and a processing pipeline that generates standardized JSON output suitable for restaurant management systems and food delivery platforms. The project also includes document preprocessing, metadata generation, validation of extracted information, and performance evaluation across diverse menu formats. The developed solution demonstrates how modern AI-driven document processing techniques can significantly reduce manual effort while improving the accuracy, consistency, and efficiency of restaurant menu digitization.



MOTIVATION
The motivation behind developing the Menu Automation System is to simplify and automate the labor-intensive process of digitizing restaurant menus. Traditional menu processing involves manually extracting menu items, categories, descriptions, and prices from images or PDF documents, which is time-consuming, error-prone, and inefficient, especially when handling menus with diverse layouts and formats. By leveraging Optical Character Recognition (OCR), Artificial Intelligence (AI), and Large Language Models (LLMs), the proposed system automatically extracts, organizes, and structures menu information into a standardized JSON format with minimal human intervention. This not only reduces processing time and operational costs but also improves data accuracy, consistency, and scalability, making it easier for restaurants and food delivery platforms to maintain up-to-date digital menus and enhance their overall operational efficiency.
1.2 PROBLEM STATEMENT
Restaurant menus are commonly available in unstructured formats such as scanned images, PDFs, or printed documents, making the process of digitizing and maintaining menu data largely manual. Extracting menu items, categories, descriptions, prices, and other relevant information from these documents requires significant time and effort and is often prone to human errors and inconsistencies. Variations in menu layouts, fonts, image quality, and document formats further increase the complexity of the task. Therefore, there is a need for an intelligent and automated system that can accurately extract, organize, and standardize menu information into a structured digital format. The proposed Menu Automation System addresses this challenge by integrating Optical Character Recognition (OCR) and Artificial Intelligence (AI) techniques to automate menu digitization, reduce manual intervention, improve data accuracy, and enable seamless integration with restaurant management and food delivery platforms.
Challenge	Impact
Weak OCR quality	Weak OCR quality may lead to misinformation.
Diverse menu layouts and designs	Fonts, table structure and different formats make it difficult to extract menu
Variations in naming conventions	Different restaurants use unique naming styles and abbreviations,
LLM interpretation	Large Language Models may occasionally misinterpret menu content, hallucinate missing information



2. OBJECTIVES
The primary objective of this project is to develop a saleable and automated menu processing pipeline that converts unstructured restaurant menu documents into a standardized JSON format while minimizing manual intervention. By automating the extraction, organization, and structuring of menu data, the system aims to reduce the time, cost, and human effort involved in manual menu digitization, while improving the accuracy, consistency, and reliability of the extracted information for seamless integration with digital restaurant management and food delivery platforms.

2.1 Tools Used
Component	Verified use
Framework	Streamlit
Language	Python 3.10
Library Used	Pandas
OCR Engine	
LLM	Google Gemini 2.5 Flash
Hardware evidence in archive	Local CPU-based validation on Intel i5-1235U
Input Format	PDF
DataBase	MongoDB
Cloud Storage for Image	Cloudinary
Image Search	Pexel, 



2.3 PROJECT CONTEXT
The Menu Automation System was developed to automate the extraction and digitization of restaurant menu information using modern AI-based document processing techniques. The project integrates PaddleOCR for text extraction, Docling for document processing, and Google Gemini 2.5 Flash for intelligent information extraction and structuring. This combination was selected because it provides an efficient workflow for processing diverse menu formats, correcting OCR inaccuracies, and generating structured output with minimal manual intervention. The primary objective of this internship was not to develop a new AI model, but to understand and implement an end-to-end automation pipeline capable of converting unstructured restaurant menus into standardized digital data.
The final system processes uploaded menu images and PDF documents through a sequential pipeline, where the extracted information is organized into a standardized JSON format, transformed into a Pandas DataFrame for validation and processing, and finally stored in MongoDB for efficient retrieval and integration with downstream applications. Cloudinary was used for secure storage and management of uploaded menu documents, while Streamlit provided an interactive user interface for uploading menus and visualizing the extracted results. The completed pipeline was evaluated on menus with varying layouts and formats, demonstrating its ability to significantly reduce manual effort while producing consistent and structured digital menu data suitable for restaurant management systems and food delivery platforms.



3. INPUT DOCUMENT DESCRIPTION

The Menu Automation System was developed and evaluated using a collection of restaurant menu documents obtained from publicly available sources and sample restaurant menus. The input documents include PDF files, scanned menus, and image formats such as JPG and PNG, representing a variety of real-world menu layouts, fonts, table structures, and image qualities. This diversity enables the system to handle different formatting styles and improve its robustness in extracting menu categories, food items, descriptions, and prices. Each uploaded document is processed through an AI-powered pipeline consisting of document parsing, Optical Character Recognition (OCR), and Large Language Model (LLM)-based information extraction. The extracted information is then converted into a standardized JSON format, transformed into a Pandas DataFrame for validation, and finally stored in MongoDB for efficient retrieval and management.


Figure 3.1: Sample restaurant menu documents used as input for evaluating the Menu Automation System. 

4. METHODOLOGY

The Menu Automation System follows a sequential AI-driven document processing pipeline to automate the extraction and digitization of restaurant menu information. Initially, users upload menu documents in PDF or image formats through a Streamlit-based interface. The uploaded files are securely stored in Cloudinary, providing centralized storage and easy accessibility during processing.
The documents are then processed using Docling to extract textual and structural information, followed by PaddleOCR to recognize text from scanned or image-based menus. The extracted text is passed to Google Gemini 2.5 Flash, which performs intelligent information extraction by identifying menu categories, food items, descriptions, prices, and other relevant details while correcting OCR inaccuracies. The generated output is structured into a standardized JSON format to ensure consistency and compatibility with downstream applications.
The JSON data is subsequently converted into a Pandas DataFrame for validation, cleaning, and preprocessing before being stored in MongoDB for efficient retrieval and management. This end-to-end pipeline minimizes manual intervention, improves extraction accuracy, and enables saleable menu digitization suitable for restaurant management systems and food delivery platforms.






5. IMPLEMENTATION AND WORK DONE

The Menu Automation System was developed as an end-to-end AI-powered solution to automate the digitization of restaurant menus and eliminate the need for manual data entry. The implementation began with the development of a user-friendly interface using Streamlit, enabling users to upload restaurant menu documents in PDF and image formats. Once uploaded, the documents were processed through PaddleOCR, which extracted textual information from menus with varying layouts, fonts, and image qualities.
The extracted text was then passed to Google Gemini 2.5 Flash, which performed intelligent information extraction by identifying menu categories, food items, descriptions, prices, and other relevant attributes. The Large Language Model (LLM) also corrected OCR inaccuracies and organized the extracted information into a predefined schema, producing a standardized JSON output. This structured representation ensured consistency across menus from different restaurants and simplified downstream processing. 
To improve data validation and manipulation, the generated JSON was converted into a Pandas DataFrame, where the extracted information was verified, cleaned, and formatted before being stored in MongoDB. This storage mechanism enabled efficient retrieval and future integration with restaurant management systems and food delivery platforms. Throughout the internship, the complete processing pipeline was designed, implemented, and tested on restaurant menus with diverse layouts and formats to evaluate its robustness and reliability. The final system successfully automated the workflow from menu upload to structured database storage, significantly reducing manual effort while improving the accuracy, consistency, and efficiency of restaurant menu digitization.

6. RESULTS AND DISCUSSION

The developed Menu Automation System successfully automated the extraction and digitization of restaurant menu information from PDF and image-based documents. The integrated pipeline, comprising Streamlit, PaddleOCR, Google Gemini 2.5 Flash, Pandas, and MongoDB, effectively processed menus with varying layouts, fonts, and document formats. PaddleOCR accurately extracted textual content from menu images, while Google Gemini 2.5 Flash intelligently identified menu categories, food items, descriptions, and prices, organizing the extracted information into a standardized JSON format. The JSON output was further converted into a Pandas DataFrame for validation and preprocessing before being stored in MongoDB, ensuring a structured and consistent database for efficient retrieval and integration with restaurant management applications.






Figure 4. F1-confidence, precision-confidence, precision-recall, and recall-confidence curves.

The experimental results demonstrated that the proposed system significantly reduced the time and manual effort required for menu digitization while improving the consistency and reliability of the extracted data. The system performed well across a wide variety of menu designs; however, challenges such as low-resolution images, complex multi-column layouts, decorative fonts, and incomplete menu information occasionally affected OCR accuracy and the quality of information extraction. Despite these limitations, the overall implementation proved to be robust and scalable, demonstrating that the combination of OCR and Large Language Models is an effective solution for automating restaurant menu digitization and generating structured digital menu data suitable for real-world applications.


7. ERROR ANALYSIS
During the implementation of the Menu Automation System, a few limitations were observed that affected the overall extraction accuracy. The primary source of errors was the OCR stage, where low-resolution images, decorative fonts, complex menu layouts, and poor scan quality occasionally resulted in incorrect or incomplete text extraction. These inaccuracies sometimes influenced the Large Language Model (LLM), leading to minor inconsistencies in identifying menu categories, food items, descriptions, prices, or generating structured JSON output. Additional validation was therefore required before converting the extracted data into a Pandas DataFrame and storing it in MongoDB. Despite these challenges, the integrated OCR-LLM pipeline produced accurate and consistent results for the majority of menu documents, demonstrating its effectiveness for automated menu digitization while highlighting opportunities for future improvements in image preprocessing, OCR accuracy, and JSON schema validation.


Figure 5. Raw and normalized confusion matrices from the final evaluation outputs.


7.1 COMPARISION WITH EXISTING WORK
Traditional menu digitization methods primarily rely on manual data entry or conventional OCR systems, which often require significant human intervention to organize extracted text into a usable format. While OCR-based solutions can recognize textual content, they generally struggle with diverse menu layouts, decorative fonts, and complex document structures, resulting in inconsistent and unstructured outputs. In contrast, the proposed Menu Automation System combines PaddleOCR with Google Gemini 2.5 Flash to perform intelligent information extraction, automatically identifying menu categories, food items, descriptions, and prices while generating standardized JSON output. Furthermore, the integration of Pandas for data validation and MongoDB for structured storage provides an end-to-end automated pipeline that minimizes manual effort, improves consistency, and enables seamless integration with restaurant management systems and food delivery platforms. Compared with existing OCR-only approaches, the proposed system offers greater automation, better handling of unstructured menu documents, and a more scalable solution for real-world menu digitization.
Aspect	Comparison summary
Reference work	Traditional OCR-based Menu Digitization Systems
Proposed model	AI-powered Menu Automation System (PaddleOCR + Google Gemini 2.5 Flash)
Purpose	Automated restaurant menu digitization and structured data extraction
Application	Restaurant Management Systems, Digital Menu Management Systems like Tshitto
Tech stacks	PaddleOCR, Google Gemini 2.5 Flash, Streamlit, Pandas, MongoDB
Dataset	Menu from Local Restaurants of Gangtok 


8. LIMITATIONS
The system's accuracy depends on the quality of the input menu documents.
Low-resolution, blurred, or poorly scanned images can reduce OCR performance.
Complex menu layouts, decorative fonts, and multi-column formats may lead to incomplete or incorrect information extraction.
Human verification may still be required for critical or ambiguous menu information.
Further improvements in image preprocessing, OCR accuracy, and JSON schema validation can enhance the overall performance and robustness of the system.

8.1 CHALLENGES FACED:
During the development of the Menu Automation System, several challenges were encountered due to the diverse nature of restaurant menu documents. Variations in menu layouts, fonts, table structures, and image quality affected the accuracy of text extraction using OCR. Designing effective prompts for the Large Language Model (LLM) to consistently identify menu categories, food items, descriptions, and prices while generating valid JSON output also required careful refinement. Additional challenges included handling OCR errors, processing incomplete or ambiguously formatted menu information, converting structured JSON into Pandas DataFrames without data loss, and ensuring data consistency before storing it in MongoDB. Integrating multiple technologies such as Streamlit, PaddleOCR, Google Gemini 2.5 Flash, Pandas, and MongoDB into a seamless end-to-end pipeline while maintaining processing efficiency and minimizing manual intervention was another significant challenge successfully addressed during the project.

8.2 LEARNING OUTCOMES:
Gained practical experience in developing an end-to-end AI-powered Menu Automation System.
Learned to implement Optical Character Recognition (OCR) for extracting text from restaurant menu images and PDF documents
Improved prompt engineering skills to generate accurate and consistent structured outputs.
Enhanced skills in integrating multiple technologies, including Streamlit, PaddleOCR, Google Gemini 2.5 Flash, Pandas, and MongoDB, into a unified workflow.


9. FUTURE SCOPE:
The Menu Automation System can be further enhanced by improving OCR accuracy through advanced image preprocessing techniques and support for more robust OCR models. Future work may include multilingual menu processing, improved LLM prompt optimization for more accurate information extraction, and automated JSON schema validation to increase data reliability. The system can also be integrated with restaurant Point-of-Sale (POS) systems, food delivery platforms, and cloud-based services to enable real-time menu updates and seamless data synchronization. Additionally, incorporating image-based food recognition, menu analytics, and recommendation features can further extend its capabilities, making it a comprehensive AI-powered solution for restaurant menu management and digital transformation.
9.1 PRACTICAL DEPLOYMENT NOTES
The Menu Automation System was developed as a Streamlit-based application and tested on a local machine to validate its end-to-end functionality. The system accepts restaurant menu documents in PDF and image formats, processes them using PaddleOCR for text extraction and Google Gemini 2.5 Flash for intelligent information extraction, and generates structured JSON output. The extracted data is converted into a Pandas DataFrame for validation before being stored in MongoDB for efficient management and retrieval. The modular architecture of the system allows individual components to be updated or replaced without affecting the overall workflow. With minor modifications, the application can be deployed on cloud platforms and integrated with restaurant management systems, Point-of-Sale (POS) software, and online food delivery platforms to provide scalable, automated, and real-time menu digitization services.
Deployment element	Target behaviour
Input source	Restaurant menu images and PDF documents uploaded by users
Processing logic	OCR-based text extraction followed by LLM-based syntactic and semantic correction, menu item extraction, and structured data generation.
Output	Standardized JSON converted to Pandas DataFrame and stored in MongoDB


CONCLUSION:
The Menu Automation System successfully demonstrated the application of Artificial Intelligence for automating the digitization of restaurant menus. By integrating PaddleOCR, Google Gemini 2.5 Flash, Streamlit, Pandas, and MongoDB, the system was able to efficiently extract, organize, and store menu information from unstructured PDF and image documents with minimal manual intervention. The implementation significantly reduced the time and effort required for manual menu digitization while improving the consistency and reliability of the extracted data through a standardized JSON-based workflow.
Overall, the project achieved its objective of developing an end-to-end automated menu processing pipeline capable of handling diverse menu formats and generating structured digital data suitable for restaurant management systems and food delivery platforms. Although certain challenges remain in handling low-quality images, complex layouts, and multilingual menus, the developed system provides a scalable and practical solution for real-world menu digitization. The knowledge and experience gained during this internship strengthened my understanding of AI-driven document processing, system integration, and workflow automation, providing a strong foundation for future work in intelligent document understanding and automation systems.

