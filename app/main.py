from decimal import Decimal

import boto3
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons

# Get service resource:
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Point")


def get_all_data(table: boto3.dynamodb.table) -> pd.DataFrame:
    items = table.scan()["Items"]
    data = {
        "x": map(lambda i: float(i["x"]), items),
        "y": map(lambda i: float(i["y"]), items),
        "class": map(lambda i: float(i["class"]), items),
        "origin": map(lambda i: i["origin"], items),
    }
    data = pd.DataFrame.from_dict(data)
    return data


def scatter(data, cls, origin, marker, ax, s, alpha, c, label):
    data = data.loc[lambda df: (df["class"] == cls) & (df["origin"] == origin)]
    ax.scatter(data["x"], data["y"], marker=marker, s=s, alpha=alpha, c=c, label=label)


st.set_page_config(layout="wide")


if __name__ == "__main__":
    dynamodb = boto3.resource("dynamodb")

    col1, col2 = st.columns(2)

    with col1:
        with st.form("prediction-form"):
            st.write("Moon Prediction")
            x_coordinate = st.number_input("X Coordinate:")
            y_coordinate = st.number_input("Y Coordinate:")

            predict = st.form_submit_button("Predict")
            if predict:
                url = "http://ai-service.default.svc.cluster.local/predict"
                payload = {"x": x_coordinate, "y": y_coordinate}
                try:
                    response = requests.post(url, json=payload)
                    st.write(
                        "X Coordinate:", x_coordinate, 
                        "Y Coordinate:", y_coordinate,
                        "Predicted Class:", response.json()["prediction"]
                    )
                except Exception as e:
                    st.error("AI service is not available. Please try again.")

        with st.form("add-form"):
            st.write("Add Data")
            x_coordinate = st.number_input("X Coordinate:")
            y_coordinate = st.number_input("Y Coordinate:")
            cls = st.number_input("Class:")

            persist = st.form_submit_button("Add")
            if persist:
                try:
                    table = dynamodb.Table("Point")
                    table.put_item(
                        Item={
                            "x": Decimal(str(x_coordinate)),
                            "y": Decimal(str(y_coordinate)),
                            "class": Decimal(str(cls)),
                            "origin": "user"
                        }
                    )
                except boto3.client("dynamodb").exceptions.ResourceInUseException as e:
                    st.error("Table 'Point' does not exist!")
                except Exception as e:
                    st.error(str(e))

    with col2:
        data = get_all_data(table)
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.xaxis.set_tick_params(labelsize=20)
        ax.yaxis.set_tick_params(labelsize=20)
        
        scatter(data, 0, "original", "o", ax, 100, 0.2, "deepskyblue", "Original 0")
        scatter(data, 1, "original", "o", ax, 100, 0.2, "orange", "Original 1")
        scatter(data, 0, "user", "X", ax, 100, 1.0, "deepskyblue", "User 0")
        scatter(data, 1, "user", "X", ax, 100, 1.0, "orange", "User 1")

        ax.legend(title="Class")
        st.pyplot(fig)