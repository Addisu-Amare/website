import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
from urllib.parse import quote
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from time import sleep
import re

# Initialize VADER analyzer
analyzer = SentimentIntensityAnalyzer()

# Page configuration
st.set_page_config(
    page_title="Gold Market Sentiment Analyzer",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FFD700;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4CAF50;
        margin-bottom: 2rem;
        text-align: center;
    }
    .sentiment-positive {
        color: #4CAF50;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
        background-color: rgba(76, 175, 80, 0.1);
    }
    .sentiment-negative {
        color: #f44336;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
        background-color: rgba(244, 67, 54, 0.1);
    }
    .sentiment-neutral {
        color: #FFA500;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
        background-color: rgba(255, 165, 0, 0.1);
    }
    .article-card {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid #FFD700;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

def fetch_article_content(url):
    """Fetch article content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:1000]  # Limit to first 1000 characters
    except Exception as e:
        return f"Content not retrieved: {str(e)}"

def fetch_news(query, num_articles=5):
    """Fetch news articles based on query"""
    rss_url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(rss_url)
        news_items = feed.entries[:num_articles]
        
        articles = []
        for item in news_items:
            # Clean title (remove source name if present)
            title = re.sub(r'\s*-\s*[^-]+$', '', item.title)
            
            # Parse published date
            published = item.get('published', 'Date not available')
            
            articles.append({
                "title": title,
                "link": item.link,
                "published": published,
                "source": item.get('source', {}).get('title', 'Unknown Source')
            })
        
        return articles
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

def analyze_sentiment(text):
    """Analyze sentiment using VADER"""
    if not text or text.isspace():
        return 0.0, 'Neutral'
    
    scores = analyzer.polarity_scores(text)
    polarity = scores['compound']
    
    if polarity > 0.05:
        sentiment = 'Positive'
    elif polarity < -0.05:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    
    return polarity, sentiment

def get_sentiment_color(sentiment):
    """Return color code for sentiment"""
    colors = {
        'Positive': '#4CAF50',
        'Negative': '#f44336',
        'Neutral': '#FFA500'
    }
    return colors.get(sentiment, '#808080')

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 GOLD MARKET SENTIMENT ANALYZER</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time Market Sentiment Analysis from News Headlines</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://www.gold.org/sites/default/files/styles/og_image/public/2021-08/gold-bars.jpg?itok=EkClB6ds", width=True)
        st.title("⚙️ Settings")
        
        # User inputs
        num_articles = st.slider("Articles per query", min_value=3, max_value=15, value=5, step=1)
        
        # Query selection
        st.subheader("🔍 Search Queries")
        default_queries = [
            "gold market",
            "gold price",
            "gold news",
            "gold trends",
            "gold analysis"
        ]
        
        queries = []
        for i, q in enumerate(default_queries):
            if st.checkbox(q, value=True, key=f"query_{i}"):
                queries.append(q)
        
        custom_query = st.text_input("Add custom query (optional)")
        if custom_query:
            queries.append(custom_query)
        
        # Analysis button
        analyze_button = st.button("🚀 Analyze Sentiment", type="primary", use_container_width=True)
        
        # Info
        with st.expander("ℹ️ About"):
            st.write("""
            This app analyzes sentiment from gold market news headlines using VADER sentiment analysis.
            
            **How it works:**
            1. Fetches latest news from Google News RSS
            2. Analyzes each headline for sentiment
            3. Aggregates results to show market sentiment
            
            **Sentiment classification:**
            - Positive: compound score > 0.05
            - Neutral: -0.05 ≤ compound ≤ 0.05
            - Negative: compound score < -0.05
            """)
    
    # Main content
    if not queries:
        st.warning("⚠️ Please select at least one query from the sidebar to begin analysis.")
        return
    
    if analyze_button:
        with st.spinner("🔄 Fetching and analyzing news articles..."):
            all_articles = []
            progress_bar = st.progress(0)
            
            for idx, query in enumerate(queries):
                # Update progress
                progress = (idx + 1) / len(queries)
                progress_bar.progress(progress)
                
                # Fetch articles
                articles = fetch_news(query, num_articles)
                all_articles.extend(articles)
                
                # Add small delay to avoid rate limiting
                sleep(0.5)
            
            if not all_articles:
                st.error("❌ No articles found. Please try different queries or try again later.")
                return
            
            # Analyze sentiment for each article
            for article in all_articles:
                polarity, sentiment = analyze_sentiment(article['title'])
                article['polarity'] = polarity
                article['sentiment'] = sentiment
            
            # Store in session state
            st.session_state['articles'] = all_articles
    
    # Display results if available
    if 'articles' in st.session_state and st.session_state['articles']:
        articles = st.session_state['articles']
        
        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        total_articles = len(articles)
        sentiment_counts = {
            'Positive': sum(1 for a in articles if a['sentiment'] == 'Positive'),
            'Negative': sum(1 for a in articles if a['sentiment'] == 'Negative'),
            'Neutral': sum(1 for a in articles if a['sentiment'] == 'Neutral')
        }
        
        avg_polarity = sum(a['polarity'] for a in articles) / total_articles if total_articles > 0 else 0
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #666;">📰 Total Articles</h3>
                <h2 style="font-size: 2.5rem;">{}</h2>
            </div>
            """.format(total_articles), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #666;">📊 Avg. Polarity</h3>
                <h2 style="font-size: 2.5rem; color: {};">{:.2f}</h2>
            </div>
            """.format(get_sentiment_color('Positive' if avg_polarity > 0.05 else 'Negative' if avg_polarity < -0.05 else 'Neutral'), avg_polarity), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #666;">📈 Market Mood</h3>
                <h2 style="font-size: 2rem; color: {};">{}</h2>
            </div>
            """.format(
                get_sentiment_color(max(sentiment_counts, key=sentiment_counts.get)),
                max(sentiment_counts, key=sentiment_counts.get)
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #666;">🎯 Confidence</h3>
                <h2 style="font-size: 2rem;">{:.0f}%</h2>
            </div>
            """.format((sentiment_counts['Positive'] + sentiment_counts['Negative']) / total_articles * 100), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie Chart
            fig_pie = px.pie(
                values=list(sentiment_counts.values()),
                names=list(sentiment_counts.keys()),
                title="Sentiment Distribution",
                color_discrete_map={'Positive': '#4CAF50', 'Negative': '#f44336', 'Neutral': '#FFA500'},
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar Chart
            fig_bar = px.bar(
                x=list(sentiment_counts.keys()),
                y=list(sentiment_counts.values()),
                title="Sentiment Counts",
                color=list(sentiment_counts.keys()),
                color_discrete_map={'Positive': '#4CAF50', 'Negative': '#f44336', 'Neutral': '#FFA500'}
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Timeline of polarities
        st.markdown("---")
        st.subheader("📊 Sentiment Polarity Timeline")
        
        df = pd.DataFrame([
            {
                'Title': a['title'][:50] + "...",
                'Polarity': a['polarity'],
                'Sentiment': a['sentiment'],
                'Source': a['source']
            }
            for a in articles
        ])
        
        fig_timeline = px.scatter(
            df,
            x=df.index,
            y='Polarity',
            color='Sentiment',
            hover_data=['Title', 'Source'],
            title="Article Sentiment Distribution",
            color_discrete_map={'Positive': '#4CAF50', 'Negative': '#f44336', 'Neutral': '#FFA500'}
        )
        fig_timeline.add_hline(y=0.05, line_dash="dash", line_color="gray", opacity=0.5)
        fig_timeline.add_hline(y=-0.05, line_dash="dash", line_color="gray", opacity=0.5)
        fig_timeline.update_layout(xaxis_title="Article Index", yaxis_title="Polarity Score")
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Articles List
        st.markdown("---")
        st.subheader("📰 Analyzed Articles")
        
        # Filter options
        sentiment_filter = st.multiselect(
            "Filter by sentiment",
            options=['Positive', 'Negative', 'Neutral'],
            default=['Positive', 'Negative', 'Neutral']
        )
        
        filtered_articles = [a for a in articles if a['sentiment'] in sentiment_filter]
        
        for idx, article in enumerate(filtered_articles):
            sentiment_class = f"sentiment-{article['sentiment'].lower()}"
            
            st.markdown(f"""
            <div class="article-card">
                <h4 style="margin-bottom: 5px;">{article['title']}</h4>
                <p style="color: #666; font-size: 0.9rem; margin-bottom: 10px;">
                    📅 {article['published']} | 📰 {article['source']}
                </p>
                <div style="display: flex; align-items: center; gap: 20px;">
                    <span class="{sentiment_class}">
                        {article['sentiment']} ({article['polarity']:.2f})
                    </span>
                    <a href="{article['link']}" target="_blank" style="color: #FFD700; text-decoration: none;">
                        Read Full Article →
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Export option
        if st.button("📥 Export Results as CSV"):
            export_df = pd.DataFrame(articles)
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"gold_sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()