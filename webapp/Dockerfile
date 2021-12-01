FROM tiangolo/meinheld-gunicorn-flask:python3.6
LABEL  maintainer="Connor Hornibrook"

## Updates and Dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    libaio1 \
    tzdata \
    libgeos-dev 
    
## Install Python dependencies
ADD requirements.txt .
RUN pip install -r requirements.txt

COPY ./app /app
RUN mkdir -p /viz
RUN mkdir -p /viz/chart
RUN mkdir -p /viz/scatterplot
RUN mkdir -p /viz/line_chart
COPY ./app/templates/blank-chart.html /viz/chart/blank-chart.html


EXPOSE 80
HEALTHCHECK --interval=2m --timeout=3s CMD curl -f http://127.0.0.1/ || exit 1