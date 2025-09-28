# ollama-RAG-LangChain   🍁

 Спасибо автору https://habr.com/ru/articles/931396/
 RAG-система на основе LangChain и Ollama
 В этом коде мы: загружаем все .txt файлы из папки, режем их на фрагменты по ~1000 символов, получаем для них эмбеддинги через OllamaEmbedding, сохраняем в локальный индекс Chroma, затем при запросе извлекаем топ-3 похожих фрагмента и передаем их вместе с вопросом в модель Ollama. Результат – сгенерированный ответ. В реальном сценарии, вместо печати, можно обернуть это в веб-сервис или чат-интерфейс.


``` bash
git clone https://github.com/SergeyMi37/ollama-rag-langchain.git
cd ollama-rag-langchain
```

Create virtual environment (optional)
``` bash
python3 -m venv env
source env/bin/activate
```

Create virtual environment for Windows
``` bash
python -m venv env
source env/Scripts/activate
```

Install all requirements:
``` bash
pip install -r requirements.txt
```

Выполнить запрос к нейронке
``` bash
python main.py 
```
Используя исходные документы, выбери номер темы, который больше всего подходит по частотному анализу слов для текста: 'Отсутствует водоснабжение'. В Ответ предоставь только номер темы.

Ответ 1: 2.2
