# Interactive Point Labeller

Interactive Point Labeller is a Dash-based application that allows users to label points in a 2D space interactively.  
It was primarily designed for annotating time series points (such as outliers, regime shifts etc.) with ease.

---

## Features
- **Drag-and-Drop CSV Upload**: Easily upload your data for annotation.
- **Interactive Point Labeling**: Click on points to cycle through annotation options.
- **Customizable Annotations**: Define your own annotation categories.
- **Download Annotated Data**: Save your labeled data as a CSV file.

---

## Getting Started

### Prerequisites
Please check the pyproject.toml to see the required dependencies.

### Installation
Clone the repository and install the required dependencies. The project uses `uv` as package manager but you
can also install the packages using pip.

```bash
uv venv
```
```bash
source venv/bin/activate
````
```bash
uv sync
```

### Running the Application
1. To run the application, execute the following command in your terminal:
```bash
python -m src.interactive_point_labeller.main
```
2. Upload Your Data:  
Drag and drop a .csv file containing your data into the app.
3. Annotate Points:
Click on points in the scatterplot to cycle through annotation options.
Download Annotated Data:
4. Download the re-labeled data
Click the "Download CSV" button to save your labeled data.
