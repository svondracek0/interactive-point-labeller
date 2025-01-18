FROM mtr.devops.telekom.de/ai_incubator/python3.12

# get python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT

CMD python -m src.main