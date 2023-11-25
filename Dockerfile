FROM continuumio/anaconda3

# 將本地端的 environment.yml 和 module.py 複製到 Docker 映像檔中
# COPY environment.yml /tmp/environment.yml
COPY module.py /app/module.py
# COPY credentials.json /event_site_project_access/credentials.json
# COPY mongodb_access.txt /event_site_project_access/mongodb_access.txt
# COPY token.json /event_site_project_access/token.json
# COPY service_account_credentials.json /event_site_project_access/service_account_credentials.json

# 透過 conda 來建立一個新的環境並安裝所需套件
# RUN conda env create -f /tmp/environment.yml && \
#    conda clean -afy

SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]

RUN conda install -c conda-forge google-api-python-client google-auth-oauthlib --yes
RUN conda install -c defaults pandas flask pymongo --yes
RUN pip install "pymongo[srv]"

# 複製 app.py 到容器中的 /app 目錄
COPY app.py /app/app.py

# 指定工作目錄
WORKDIR /app

# 在容器啟動時執行 app.py
CMD ["python", "app.py"]