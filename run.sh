#!/bin/bash
# 化学安全审查智能体 - 启动脚本

cd /data/zhw/demo/chem_safety/chemical_safety_agent

# 使用 zhw_p 环境启动 Streamlit
/data/zhw/conda_envs/zhw_p/bin/streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --browser.serverAddress localhost
