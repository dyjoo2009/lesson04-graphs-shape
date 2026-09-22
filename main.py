import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "1년간 박스오피스 10위권에 든 영화 가운데 이 기간에 개봉한 216편의 요약 데이터를 "
    "다양한 그래프로 살펴봅니다."
)


# -----------------------------
# 데이터 불러오기
# -----------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # openDt: 여덟 자리 숫자 -> 날짜형으로 변환
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d", errors="coerce")

    # genre: 세로막대 기호(|)로 여러 개 적힌 경우 첫 번째 장르만 사용
    df["genre"] = df["genre"].astype(str).apply(lambda x: x.split("|")[0].strip())

    return df


df = load_data()

with st.expander("원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()


# =====================================================
# 1. 장르별 영화 편수 - 도넛 그래프
# =====================================================
st.header("1. 장르별 영화 편수")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]
genre_counts["ratio"] = genre_counts["count"] / genre_counts["count"].sum() * 100

fig_genre = go.Figure(
    data=[
        go.Pie(
            labels=genre_counts["genre"],
            values=genre_counts["count"],
            hole=0.5,
            hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
            textinfo="label+percent",
        )
    ]
)
fig_genre.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    legend_title_text="장르",
)

st.plotly_chart(fig_genre, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.divider()


# =====================================================
# 2. 장르 안의 영화별 총 관객 - 트리맵
# =====================================================
st.header("2. 장르별 영화의 총 관객수")

fig_treemap = go.Figure(
    data=[
        go.Treemap(
            labels=df["movieNm"],
            parents=df["genre"],
            values=df["total_audi"],
            branchvalues="total",
            hovertemplate="영화명: %{label}<br>총 관객: %{value:,}명<extra></extra>",
        )
    ]
)
fig_treemap.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.divider()


# =====================================================
# 3. 총 관객수 분포 - 히스토그램
# =====================================================
st.header("3. 총 관객수 분포")

fig_hist = go.Figure(
    data=[
        go.Histogram(
            x=df["total_audi"],
            hovertemplate="구간: %{x}<br>영화 수: %{y}편<extra></extra>",
        )
    ]
)
fig_hist.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis_title="총 관객수",
    yaxis_title="영화 편수",
)

st.plotly_chart(fig_hist, use_container_width=True)

# 히스토그램 계산 결과로 가장 영화가 몰린 구간 찾기
counts, bin_edges = np.histogram(df["total_audi"], bins=10)
max_bin_idx = counts.argmax()
bin_start, bin_end = bin_edges[max_bin_idx], bin_edges[max_bin_idx + 1]

# 총 관객수가 가장 많은 영화
top_movie = df.loc[df["total_audi"].idxmax()]

st.markdown(
    f"**이 그래프로 알 수 있는 것:** 대부분의 영화는 총 관객수 "
    f"**{bin_start:,.0f}명 ~ {bin_end:,.0f}명** 구간에 몰려 있으며(총 {counts[max_bin_idx]}편), "
    f"총 관객수가 가장 많은 영화는 **'{top_movie['movieNm']}'**"
    f"(약 {top_movie['total_audi']:,.0f}명)입니다."
)

st.divider()


# =====================================================
# 4. 개봉일 스크린수 vs 총 관객 - 산점도
# =====================================================
st.header("4. 개봉일 스크린수와 총 관객의 관계")

fig_scatter = go.Figure()

for genre_name, group in df.groupby("genre"):
    fig_scatter.add_trace(
        go.Scatter(
            x=group["first_scrn"],
            y=group["total_audi"],
            mode="markers",
            name=genre_name,
            text=group["movieNm"],
            hovertemplate="영화명: %{text}<br>개봉일 스크린수: %{x:,}개<br>총 관객: %{y:,}명<extra></extra>",
        )
    )

fig_scatter.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객수",
    legend_title_text="장르",
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.divider()


# =====================================================
# 5. 영화 10편 이상 장르의 총 관객 분포 - 박스플롯
# =====================================================
st.header("5. 장르별 총 관객수 분포 (10편 이상 장르)")

genre_size = df["genre"].value_counts()
major_genres = genre_size[genre_size >= 10].index
df_major = df[df["genre"].isin(major_genres)]

fig_box = go.Figure()

for genre_name, group in df_major.groupby("genre"):
    fig_box.add_trace(
        go.Box(
            y=group["total_audi"],
            name=genre_name,
            text=group["movieNm"],
            boxpoints="outliers",
            hovertemplate="영화명: %{text}<br>총 관객: %{y:,}명<extra></extra>",
        )
    )

fig_box.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis_title="장르",
    yaxis_title="총 관객수",
    showlegend=False,
)

st.plotly_chart(fig_box, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.divider()


# =====================================================
# 6. 개봉일 스크린수 vs 총 관객 (버블 크기: 첫 주 관객)
# =====================================================
st.header("6. 개봉일 스크린수와 총 관객의 관계 - 버블 그래프")

fig_bubble = go.Figure()

# 버블 크기 스케일링을 위한 기준값
max_first_week = df["first_week_audi"].max()

for genre_name, group in df.groupby("genre"):
    fig_bubble.add_trace(
        go.Scatter(
            x=group["first_scrn"],
            y=group["total_audi"],
            mode="markers",
            name=genre_name,
            text=group["movieNm"],
            customdata=group["first_week_audi"],
            marker=dict(
                size=group["first_week_audi"],
                sizemode="area",
                sizeref=2.0 * max_first_week / (40.0 ** 2),
                sizemin=3,
            ),
            hovertemplate=(
                "영화명: %{text}<br>"
                "개봉일 스크린수: %{x:,}개<br>"
                "총 관객: %{y:,}명<br>"
                "첫 주 관객: %{customdata:,}명<extra></extra>"
            ),
        )
    )

fig_bubble.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객수",
    legend_title_text="장르",
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.divider()


# =====================================================
# 7. 제작 국가 - 장르 선버스트
# =====================================================
st.header("7. 제작 국가별 장르 구성")

nation_genre_counts = df.groupby(["nation", "genre"]).size().reset_index(name="count")

# 선버스트 계층 구성: 최상위(국가) -> 하위(장르)
labels = []
parents = []
values = []
ids = []

for nation_name, group in nation_genre_counts.groupby("nation"):
    nation_total = group["count"].sum()
    labels.append(nation_name)
    parents.append("")
    values.append(nation_total)
    ids.append(nation_name)

    for _, row in group.iterrows():
        genre_id = f"{nation_name}-{row['genre']}"
        labels.append(row["genre"])
        parents.append(nation_name)
        values.append(row["count"])
        ids.append(genre_id)

fig_sunburst = go.Figure(
    data=[
        go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            hovertemplate="%{label}<br>편수: %{value}편<extra></extra>",
        )
    ]
)
fig_sunburst.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.divider()


# =====================================================
# (다음 그래프는 여기에 같은 형식으로 추가)
# =====================================================
