import pandas as pd
import numpy as np
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_data
def load_careers():
    return pd.read_csv("data/career_data.csv")

def recommend_careers(student_skill_weights: dict, top_n=5):
    careers = load_careers()
    if not student_skill_weights:
        return pd.DataFrame()
    student_weights = {k.strip().lower(): float(v) for k, v in student_skill_weights.items() if k.strip()}
    career_skills_list = [[s.strip().lower() for s in str(sk).split(",") if s.strip()] for sk in careers["skills"]]
    vocab = sorted(set(student_weights.keys()).union(*career_skills_list))
    vocab_index = {skill: i for i, skill in enumerate(vocab)}
    student_vec = np.zeros((1, len(vocab)))
    for skill, weight in student_weights.items():
        if skill in vocab_index:
            student_vec[0, vocab_index[skill]] = weight
    career_vecs = np.zeros((len(careers), len(vocab)))
    for row_idx, skills in enumerate(career_skills_list):
        for skill in skills:
            career_vecs[row_idx, vocab_index[skill]] = 1.0
    similarities = cosine_similarity(student_vec, career_vecs)[0]
    results = careers.copy()
    results["match_percentage"] = np.clip((similarities * 100), 0, 100).round(1)
    student_skill_set = set(student_weights.keys())
    results["matched_skills"] = [sorted(student_skill_set & set(sk)) for sk in career_skills_list]
    results["missing_skills"] = [sorted(set(sk) - student_skill_set) for sk in career_skills_list]
    return results.sort_values(by="match_percentage", ascending=False).head(top_n).reset_index(drop=True)
