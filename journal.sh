# venv
python3 -m venv venv_geolife
source venv_geolife/bin/activate

# pip
pip install pandas ipykernel numpy matplotlib seaborn plotly dash geopy geopandas python-dotenv st-dbscan
pip install nbformat


# gitignore
touch .gitignore
echo ".env" >> .gitignore
echo "venv_*" >> .gitignore
echo "key*" >> .gitignore
echo "*.zip" >> .gitignore
echo "z_*" >> .gitignore
echo "data/*" >> .gitignore
echo "output/*" >> .gitignore

# .env
touch .env && code .env

# git
git init
git branch -m main
git add .
git commit -m "1st commit"

