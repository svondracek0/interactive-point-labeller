FROM python:3.12


# get python dependencies

ENV PORT=8050

COPY . .

RUN pip install .


EXPOSE $PORT

# Command to run the application
CMD ["python", "-m", "src.interactive_point_labeller.main"]