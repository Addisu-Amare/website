@echo off
echo Installing Gold Market Sentiment Analyzer with compatible versions...
echo.

echo Creating conda environment...
conda create -n mysentiment python=3.10 -y

echo Activating environment...
call conda activate mysentiment

echo Installing numpy first (specific version)...
pip install numpy==1.26.4

echo Installing PyTorch (CPU version)...
pip install torch==2.7.0 --index-url https://download.pytorch.org/whl/cpu

echo Installing remaining packages...
pip install streamlit==1.31.0
pip install pandas==2.2.0
pip install plotly==5.18.0
pip install transformers==4.51.3
pip install vaderSentiment==3.3.2
pip install textblob==0.19.0
pip install feedparser==6.0.11
pip install beautifulsoup4==4.13.4
pip install requests==2.32.3
pip install pytest==7.4.4 pytest-mock==3.12.0 pytest-cov==4.1.0

echo.
echo Installing remaining dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo Setup complete! To run the app:
echo conda activate mysentiment
echo streamlit run app.py
echo.
pause