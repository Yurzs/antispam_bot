FROM python:3.9
ADD antispam_userbot /code/antispam_userbot
ADD requirements.txt /code/
WORKDIR /code/antispam_userbot/
ENV PYTHONPATH /code/
RUN pip install -r /code/requirements.txt
CMD ["python", "bot.py"]
