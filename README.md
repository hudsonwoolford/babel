# Babel

A book dating app for tailored recommendations.

## Description

I originally created Babel for my English teacher, who was struggling to recommend books that catered to the diverse and unique interests of her students. Babel uses a dating-apps style interface, where users swipe left and right on titles, to curate specific recommendations. It implements the Linear Upper Confidence Bound (LinUCB) recommender system to ensure the suggestions both exploit and explore user preferences. Swipe sessions are limited to 20-swipes, after which a summary is displayed of liked books. Users can favourite these books for them to appear in their library. A search page also allows users to favourite specific titles. The application is intended to function as a progressive web app for mobile. Currently, Babel is being trialed in my school library for students.

## Getting Started

### Dependencies

This project was developed on a Windows 11 computer.
A full list of python libraries can be found in requirements.txt, but an overview of the main libraries is also given below.

| numpy | Math operations, including matrix and vector functionality |
| flask | Webpages and python integration |
| scikit-learn | Principal component analysis and normalisation functions |
| sentence transformers | Sentence embedding model for book vectors |

### Installing

Clone the repository. Create a virtual environment. Install the packages from requirements.txt.

Note that by default this repository only includes a sample of books (5000 titles). To configure with program with a larger catalogue, create a .env file and add a Hardcover API key to a HARDCOVER_AUTHORIZATION variable. Then run src/hardcover_api.py.
```
python src/hardcover_api --folder-path [FOLDER_PATH] --num-books [NUMBER OF BOOKS]
```

### Executing program

After configuring the virtual environment, run the src/app.py.
```
python src/app.py
```

Flask should host the application on a local port.

## Repository structure

```
src                  # master folder of the app's functionality
 ├───alternate       # old scripts for alternate use cases
 ├───depreceated     # depreceated scripts from old features
 ├───static          # css style sheets
 └───templates       # flask templates / web-pages
     └───icons       # svg icons for application
```

## Acknowledgments

[Hardcover API](https://docs.hardcover.app/)
[Sentence Transformers Model](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[LinUCB](https://arxiv.org/pdf/1003.0146)
[Flask](https://flask.palletsprojects.com/en/stable/)
[Raspberry Pi](https://www.raspberrypi.com/)
[Cloudflare](https://www.cloudflare.com/)