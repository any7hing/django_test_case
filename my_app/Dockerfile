FROM python
# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /src
# Копируем файл requirements.txt внутрь контейнера
COPY requirements.txt ./
# Устанавливаем зависимости, описанные в файле requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONNONBUFFERED 1
COPY . .

RUN pip install -r requirements.txt