import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

import os
current_dir = os.path.dirname(os.path.abspath(__file__))

df_ah = pd.read_csv(f'{current_dir}/datas/发电侧日前出清结果.csv')
df_rl = pd.read_csv(f'{current_dir}/datas/发电侧实时出清结果.csv')



unit_list = list(set(df_ah['交易单元名称'].unique().tolist() + df_ah['交易单元名称'].unique().tolist()))

time_groups = {
        '2024年前3次现货试运行': ('2024-01-01', '2024-10-30'),
        '2024年11月现货试运行': ('2024-10-31', '2024-12-01'),
        '2025年05月现货试运行': ('2025-05-01', '2025-05-20')
}


def scatter_by_time_groups(df, x_col, y_col, time_col, time_groups, unit, pt, fig=None):
    if pt == '日前':
        sym = 'circle-open'
    else:
        sym = 'x'
    # 按指定时间区间分组绘制不同颜色
    if fig is None:
        fig = go.Figure()

    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']

    for i, (group_name, (start_date, end_date)) in enumerate(time_groups.items()):
        # 筛选时间范围内的数据
        mask = (pd.to_datetime(df[time_col]) >= start_date) & \
               (pd.to_datetime(df[time_col]) <= end_date)
        group_data = df[mask]

        if not group_data.empty:
            fig.add_trace(go.Scatter(
                x=group_data[x_col], y=group_data[y_col],
                mode='markers',
                name=group_name + ' ' + pt,
                marker=dict(color=colors[i % len(colors)],
                            size=8,
                            symbol=sym
                            ),
                customdata=group_data[time_col],
                hovertemplate='<b>Volume:</b> %{x:.1f}<br>' +
                              '<b>Price:</b> %{y:.1f}<br>' +
                              '<b>Time:</b> %{customdata|%Y-%m-%d %H:%M}<br>' +
                              f'<b>Type:</b> {pt}<br>' +
                              '<extra></extra>'
            ))

    fig.update_layout(
        title=unit,
        xaxis_title='volume',
        yaxis_title='price',
        template='plotly_dark',
        hovermode='closest'
    )

    # fig.show()
    return fig


def create_unit_fig(df_ahead, df_real, unit):
    df = df_ahead[df_ahead['交易单元名称'] == unit]
    df = df[df['volume'] > 0]
    if not df.empty:
        fig = scatter_by_time_groups(df, 'volume', 'price', 'time_run', time_groups, unit, '日前')
    df = df_real[df_real['交易单元名称'] == unit]
    df = df[df['volume'] > 0]
    if not df.empty:
        fig = scatter_by_time_groups(df, 'volume', 'price', 'time_run', time_groups, unit, '实时', fig=fig)
    return fig





# 页面配置
st.set_page_config(
    page_title="燃煤电厂量价数据",
    page_icon="📊",
    layout="wide"
)

# 标题
st.title("📊 燃煤电厂量价数据")

# 侧边栏控制
st.sidebar.header("控制面板")




# 侧边栏选择控件
st.sidebar.subheader("选择图表")


selected_charts = st.sidebar.multiselect(
    "选择要显示的图表:",
    options=unit_list,
    default=unit_list
)



if not selected_charts:
    st.warning("请在左侧选择至少一个图表!")
else:
    chart_functions = {}
    for unit in unit_list:
        try:
            with st.container():
                fig = create_unit_fig(df_ah, df_rl, unit)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            print(e)

