# Gold Market Sentiment Analyzer - Web Scraping for Sentiment Analysis

A real-time web scraping and sentiment analysis application that monitors gold market news and provides instant market sentiment insights.

## **Project Overview**

This application combines **web scraping** and **sentiment analysis** to automatically fetch gold market news from Google News RSS and analyze the emotional tone of headlines, providing traders and investors with quick market sentiment insights.

### **What is Web Scraping for Sentiment Analysis?**

Web scraping for sentiment analysis is the process of:
1. **Automatically collecting** text data from websites (news articles, social media, etc.)
2. **Analyzing the emotional tone** of that text (positive, negative, neutral)
3. **Aggregating results** to understand overall public sentiment about a topic

In this project, we scrape gold market news headlines and analyze whether the market mood is bullish (positive), bearish (negative), or neutral.

## **Code Overview**

### **Purpose**
A Streamlit web app that fetches gold market news and analyzes their sentiment (positive/negative/neutral) using VADER sentiment analysis.

### **Main Components**

#### **1. Setup & Configuration**
- Uses **VADER SentimentIntensityAnalyzer** for sentiment analysis
- Streamlit page config with title "Gold Market Sentiment Analyzer"
- Custom CSS styling for visual appeal

#### **2. Core Functions**

| Function | What it does |
|----------|-------------|
| `fetch_news(query, num_articles)` | Gets gold news from Google News RSS feed |
| `fetch_article_content(url)` | Retrieves full article text (limited to 1000 chars) |
| `analyze_sentiment(text)` | Returns polarity score (-1 to 1) and sentiment label |
| `get_sentiment_color(sentiment)` | Returns color code for UI |

#### **3. Sentiment Logic**
```python
if polarity > 0.05 → "Positive" (green)
if polarity < -0.05 → "Negative" (red)
else → "Neutral" (orange)
```

#### **4. User Interface**

**Sidebar:**
- Select search queries (gold market, price, news, etc.)
- Choose number of articles per query
- "Analyze Sentiment" button

**Main Display:**
- **4 Metric Cards**: Total articles, avg polarity, market mood, confidence %
- **2 Charts**: Pie chart + bar chart of sentiment distribution
- **Timeline**: Scatter plot of article polarities
- **Article List**: Filterable by sentiment with links to sources
- **Export**: Download results as CSV

#### **5. Data Flow**
1. User selects queries → clicks Analyze
2. App fetches news from Google RSS
3. Analyzes each headline with VADER
4. Stores results in session state
5. Displays visualizations and article list
6. Allows CSV export

### **Key Libraries Used**
- `streamlit` - Web app framework
- `vaderSentiment` - Sentiment analysis
- `feedparser` - RSS feed parsing
- `plotly` - Interactive charts
- `pandas` - Data manipulation
- `beautifulsoup4` - HTML parsing for article content
- `requests` - HTTP requests for web scraping

## **How to Reproduce and Use**

### **Prerequisites**
- Python 3.10
- Conda (recommended) or virtualenv
- Git (optional)

### **Installation Steps**

#### **Option 1: Using Conda (Recommended)**

```bash
# 1. Clone or download the repository
git clone <repository-url>
cd gold_sentiment

# 2. Create conda environment
conda create -n mysentiment python=3.10 -y

# 3. Activate the environment
conda activate mysentiment

# 4. Install pip (if needed)
conda install pip

# 5. Install requirements
pip install -r requirements.txt
```

#### **Option 2: Using Virtualenv**

```bash
# 1. Create virtual environment
python -m venv mysentiment

# 2. Activate it (Windows)
mysentiment\Scripts\activate

# Or on Mac/Linux:
# source mysentiment/bin/activate

# 3. Install requirements
pip install -r requirements.txt
```

### **Running the Application**

```bash
# Make sure your environment is activated
conda activate mysentiment

# Run the Streamlit app
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

### **Running Tests**

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest test_app.py -v
```

## **Project Structure**

```
gold_sentiment/
├── app.py                          # Main Streamlit application
├── test_app.py                      # Unit tests
├── test_sentiment_edge_cases.py     # Edge case tests
├── requirements.txt                  # Dependencies
├── pytest.ini                        # Pytest configuration
├── .coveragerc                       # Coverage configuration
├── README.md                          # Documentation
├── setup.bat                          # Windows setup script
├── setup.sh                           # Mac/Linux setup script
└── verify_install.py                  # Installation verification
```

## **How Web Scraping Works in This App**

1. **RSS Feed Scraping**: The app sends a query to Google News RSS
   ```
   https://news.google.com/rss/search?q=gold+market
   ```

2. **HTML Parsing**: When needed, `BeautifulSoup` extracts full article content
   ```python
   soup = BeautifulSoup(response.text, 'html.parser')
   paragraphs = soup.find_all('p')
   ```

3. **Text Extraction**: Cleans HTML and extracts readable text
   - Removes scripts, styles
 - Gets paragraph text
   - Limits to 1000 characters for performance

## **Sentiment Analysis in Detail**

VADER (Valence Aware Dictionary and sEntiment Reasoner) is specifically tuned for social media and news text:

- **Lexicon-based**: Uses a dictionary of words with sentiment scores
- **Handles**: Emojis, slang, capitalization, punctuation
- **Output**: Compound score from -1 (most negative) to +1 (most positive)

Example:
```python
"Gold prices surge to record high!" → Compound: 0.8 → Positive
"Gold market crashes amid uncertainty" → Compound: -0.7 → Negative
"Gold prices remain stable today" → Compound: 0.0 → Neutral
```

## **Troubleshooting**

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| NumPy version conflict | Use numpy==1.26.4 (not 2.x) |
| PyTorch installation | Use CPU version: `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| RSS feed not working | Check internet connection; Google may block automated requests |
| No articles found | Try different search queries or increase article count |

### Verify Installation

Run the verification script:
```bash
python verify_install.py
```

## **Use Cases**

- **Traders**: Quick market sentiment check before trading
- **Investors**: Monitor news sentiment for investment decisions
- **Researchers**: Analyze media sentiment trends
- **Students**: Learn web scraping and NLP techniques

## **Customization Options**

You can modify the app to:
- Track different commodities (silver, oil, etc.)
- Use different news sources
- Adjust sentiment thresholds
- Add more visualization types
- Include historical sentiment tracking

## **Performance Considerations**

- **Rate Limiting**: Includes 0.5s delays between requests
- **Content Limits**: Article content limited to 1000 chars
- **Caching**: Session state stores results temporarily
- **Error Handling**: Graceful failure for network issues

- ## Relevance to Financial Inclusion

This project demonstrates the core skills needed for alternative data research:
- **Data Discovery**: Identifying sentiment signals from unstructured news
- **Signal Engineering**: Converting raw text into structured polarity scores
- **Operationalization**: Building a real-time, production-ready dashboard
- **Decision Support**: Visualizing insights for quick, informed decisions

This approach can be extended to:
- Mobile money transaction sentiment
- Agricultural market news analysis
- Small business health indicators from social media

## **License**

MIT License - Feel free to use, modify, and distribute.

---

Happy Analyzing!  

*Remember: Sentiment analysis is a tool, not financial advice. Always do your own research before making investment decisions.*
