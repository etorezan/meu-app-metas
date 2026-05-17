import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Gestão de Metas Quadrimestrais", layout="wide")
st.title("✈️ Sistema Integrado de Metas e Localizadores - Azul")

FICHEIRO_VENDAS = "vendas_quadrimestre.csv"
FICHEIRO_EQUIPA = "equipa_consultores.csv"

# 2. INICIALIZAÇÃO AUTOMÁTICA DO SISTEMA COM OS TEUS DADOS ATUALIZADOS
def inicializar_sistema():
    if not os.path.exists(FICHEIRO_EQUIPA):
        pd.DataFrame({"Nome": ["Isabelle", "Luciana", "Euclides"]}).to_csv(FICHEIRO_EQUIPA, index=False)
        
    if not os.path.exists(FICHEIRO_VENDAS):
        dados_atualizados = [
            # SEMANA 01
            {"Quadrimestre": "2º Quad (Maio-Agosto 2026)", "Semana": "Semana 01", "Participante": "Isabelle", "Localizador": "LOCS01A", "Vendas Azul": 51698.74, "Vendas Geral": 1390.85},
            {"Quadrimestre": "2º Quad (Maio-Agosto 2026)", "Semana": "Semana 01", "Participante": "Luciana", "Localizador": "LOCS01B", "Vendas Azul": 7737.67, "Vendas Geral": 28195.29},
            {"Quadrimestre": "2º Quad (Maio-Agosto 2026)", "Semana": "Semana 01", "Participante": "Euclides", "Localizador": "LOCS01C", "Vendas Azul": 20920.00, "Vendas Geral": 0.0},
            # SEMANA 02
            {"Quadrimestre": "2º Quad (Maio-Agosto 2026)", "Semana": "Semana 02", "Participante": "Luciana", "Localizador": "LOCS02A", "Vendas Azul": 78730.40, "Vendas Geral": 50024.01},
            {"Quadrimestre": "2º Quad (Maio-Agosto 2026)", "Semana": "Semana 02", "Participante": "Euclides", "Localizador": "LOCS02B", "Vendas Azul": 48793.11, "Vendas Geral": 0.0},
            {"Quadrimestre": "2º Quad (Maio-Agosto 2026)", "Semana": "Semana 02", "Participante": "Isabelle", "Localizador": "LOCS02C", "Vendas Azul": 38367.08, "Vendas Geral": 6390.36},
        ]
        pd.DataFrame(dados_atualizados).to_csv(FICHEIRO_VENDAS, index=False)

inicializar_sistema()

# Carregar dados
df_equipa = pd.read_csv(FICHEIRO_EQUIPA)
lista_consultores = df_equipa["Nome"].tolist()
df_vendas = pd.read_csv(FICHEIRO_VENDAS)

TOTAL_SEMANAS = 16  
semanas_lista = [f"Semana {i:02d}" for i in range(1, TOTAL_SEMANAS + 1)]

# CÁLCULO AUTOMÁTICO DA SEMANA VIGENTE
def calcular_semana_atual():
    data_atual = datetime.now()
    inicio_quad = datetime(2026, 5, 1)
    if data_atual >= inicio_quad:
        dias_passados = (data_atual - inicio_quad).days
        semana_num = (dias_passados // 7) + 1
        if semana_num <= TOTAL_SEMANAS:
            return f"Semana {semana_num:02d}"
    return "Semana 01"

semana_padrao = calcular_semana_atual()

# 3. PAINEL LATERAL: CONFIGURAÇÃO DE METAS E PERÍODOS
st.sidebar.header("⚙️ Configurações de Período")

quadrimestre_ativo = st.sidebar.selectbox("Quadrimestre de Trabalho:", [
    "2º Quad (Maio-Agosto 2026)", 
    "1º Quad (Janeiro-Abril)", 
    "3º Quad (Setembro-Dezembro)"
])

nivel_alvo = st.sidebar.selectbox("Alvo da Agência para o Período:", [
    "Azul Celeste (R$ 451.077)", 
    "Azul Turquesa (R$ 1.292.529)", 
    "Azul Royal (R$ 2.817.895)", 
    "Azul Infinito (R$ 10.523.249)"
], index=2)

valores_alvo = {
    "Azul Celeste (R$ 451.077)": 451077.0,
    "Azul Turquesa (R$ 1.292.529)": 1292529.0,
    "Azul Royal (R$ 2.817.895)": 2817895.0,
    "Azul Infinito (R$ 10.523.249)": 10523249.0
}
META_GLOBAL_QUAD = valores_alvo[nivel_alvo]
meta_base_pura_semana = META_GLOBAL_QUAD / TOTAL_SEMANAS

# 4. PAINEL LATERAL: CADASTRAR CONSULTOR
st.sidebar.markdown("---")
with st.sidebar.expander("👤 Cadastrar Novo Colaborador"):
    novo_consultor = st.text_input("Nome do Novo Consultor:").strip()
    if st.button("Adicionar à Equipa"):
        if novo_consultor and novo_consultor not in lista_consultores:
            nova_equipa = pd.concat([df_equipa, pd.DataFrame({"Nome": [novo_consultor]})], ignore_index=True)
            nova_equipa.to_csv(FICHEIRO_EQUIPA, index=False)
            st.success(f"✅ {novo_consultor} adicionado!")
            st.rerun()

# 5. PAINEL LATERAL: LANÇAMENTO DE VENDAS
st.sidebar.markdown("---")
st.sidebar.header("📝 Lançamento de Vendas")

with st.sidebar.form(key="form_vendas_novas"):
    semana_sel = st.selectbox("Semana do Registo:", semanas_lista, index=semanas_lista.index(semana_padrao))
    consultor_sel = st.selectbox("Consultor Responsável:", lista_consultores)
    localizador_sel = st.text_input("Localizador da Reserva:").strip().upper()
    venda_azul = st.number_input("Valor na Azul (R$):", min_value=0.0, format="%.2f")
    venda_geral = st.number_input("Valor Geral/Outros (R$):", min_value=0.0, format="%.2f")
    confirmacao = st.checkbox("Confirmo os valores inseridos.")
    botao_enviar = st.form_submit_button("Gravar Venda")

if botao_enviar:
    localizador_existe = df_vendas["Localizador"].astype(str).str.upper() == localizador_sel
    if not localizador_sel or not confirmacao:
        st.sidebar.error("⚠️ Preencha o localizador e valide a confirmação.")
    elif localizador_existe.any():
        venda_duplicada = df_vendas[localizador_existe].iloc[0]
        st.sidebar.error(f"❌ **Erro!** Localizador já cadastrado por {venda_duplicada['Participante']} na {venda_duplicada['Semana']}.")
    else:
        nova_venda_dict = {
            "Quadrimestre": quadrimestre_ativo, "Semana": semana_sel, "Participante": consultor_sel,
            "Localizador": localizador_sel, "Vendas Azul": venda_azul, "Vendas Geral": venda_geral
        }
        df_vendas = pd.concat([df_vendas, pd.DataFrame([nova_venda_dict])], ignore_index=True)
        df_vendas.to_csv(FICHEIRO_VENDAS, index=False)
        st.sidebar.success("✅ Venda integrada!")
        st.rerun()

df_vendas_quad = df_vendas[df_vendas["Quadrimestre"] == quadrimestre_ativo]

# 6. CÁLCULO DAS METAS ROLANTES SEMANAIS COLETIVAS
metas_semanais_calculadas = {}
acumulado_deficit_geral = 0.0

for sem in semanas_lista:
    meta_base_agencia_semana = meta_base_pura_semana + acumulado_deficit_geral
    metas_semanais_calculadas[sem] = max(meta_base_agencia_semana, 0.0)
    vendas_reais_semana = df_vendas_quad[df_vendas_quad["Semana"] == sem]["Vendas Azul"].sum()
    df_semana_teste = df_vendas_quad[df_vendas_quad["Semana"] == sem]
    
    if not df_semana_teste.empty:
        acumulado_deficit_geral = meta_base_agencia_semana - vendas_reais_semana
    else:
        acumulado_deficit_geral = meta_base_agencia_semana - vendas_reais_semana

# 7. INDICADORES DO TOPO
st.subheader(f"📅 Monitorização: {quadrimestre_ativo}")
total_azul_quad_atual = df_vendas_quad["Vendas Azul"].sum()
percentual_quad = min(total_azul_quad_atual / META_GLOBAL_QUAD, 1.0) if META_GLOBAL_QUAD > 0 else 0.0

col_top1, col_top2, col_top3 = st.columns(3)
col_top1.metric("Faturado no Quadrimestre (Azul)", f"R$ {total_azul_quad_atual:,.2f}")
col_top2.metric("Meta Total do Período", f"R$ {META_GLOBAL_QUAD:,.2f}")
col_top3.metric("Consultores Ativos na Meta", f"{len(lista_consultores)} pessoas")
st.progress(percentual_quad, text=f"Progresso de Meta do Quadrimestre: {percentual_quad*100:.1f}%")
st.markdown("---")

# 8. ABAS DIDÁTICAS
aba_semana, aba_quadrimestre = st.tabs(["📊 Visão Semanal & Lançamentos", "🔍 Raio-X Completo do Quadrimestre"])

# ==================== ABA 1: VISÃO SEMANAL ====================
with aba_semana:
    semana_visualizar = st.selectbox("Selecione a Semana para Análise Detalhada:", semanas_lista, index=semanas_lista.index(semana_padrao))
    meta_coletiva_semana_atual = metas_semanais_calculadas.get(semana_visualizar, meta_base_pura_semana)
    meta_individual_semana_atual = meta_coletiva_semana_atual / len(lista_consultores)
    
    # INDICADOR DE META ORIGINAL PURA SEM HISTÓRICO ROLANTE (Ex: R$ 58.706,15 por consultor no plano Royal)
    meta_individual_original_estatica = meta_base_pura_semana / len(lista_consultores)

    df_da_semana = df_vendas_quad[df_vendas_quad["Semana"] == semana_visualizar]
    total_azul_sem = df_da_semana["Vendas Azul"].sum()
    total_geral_sem = df_da_semana["Vendas Geral"].sum()

    st.markdown(f"#### 📈 Desempenho — {semana_visualizar}")
    st.markdown(f"**Meta Geral Corrente (Com Reajuste):** R$ {meta_coletiva_semana_atual:,.2f} | **Meta Alvo Original Limpa (Sem Atrasos):** R$ {meta_base_pura_semana:,.2f}")
    
    if meta_coletiva_semana_atual > 0:
        pct_coletiva = min(total_azul_sem / meta_coletiva_semana_atual, 1.0)
        pct_texto_coletivo = (total_azul_sem / meta_coletiva_semana_atual) * 100
    else:
        pct_coletiva = 1.0
        pct_texto_coletivo = 100.0
        
    st.progress(pct_coletiva, text=f"Progresso Global da Agência nesta semana: {pct_texto_coletivo:.1f}%")
    st.markdown(" ")

    c_sem1, c_sem2, c_sem3 = st.columns(3)
    c_sem1.metric("Vendas Azul da Semana", f"R$ {total_azul_sem:,.2f}", delta=f"R$ {total_azul_sem - meta_coletiva_semana_atual:,.2f} vs Meta Atual")
    c_sem2.metric("Vendas Fora da Azul", f"R$ {total_geral_sem:,.2f}")
    c_sem3.metric("Faturação Bruta", f"R$ {total_azul_sem + total_geral_sem:,.2f}")

    # 9. CARTÕES INDIVIDUAIS COM AS DUAS BARRAS (ATUALIZADA VS ORIGINAL)
    st.markdown("##### 👥 Situação Atualizada por Consultor")
    colunas_consultores = st.columns(len(lista_consultores))
    
    for idx, consultor in enumerate(lista_consultores):
        df_consultor_sem = df_da_semana[df_da_semana["Participante"] == consultor]
        vendas_azul_con = df_consultor_sem["Vendas Azul"].sum()
        vendas_geral_con = df_consultor_sem["Vendas Geral"].sum()
        
        with colunas_consultores[idx]:
            st.markdown(f"### 👤 {consultor}")
            
            # --- BARRA 1: META ATUALIZADA (COM O PREJUÍZO ACUMULADO) ---
            if meta_individual_semana_atual > 0:
                pct_conclusao_atual = min(vendas_azul_con / meta_individual_semana_atual, 1.0)
                pct_texto_atual = (vendas_azul_con / meta_individual_semana_atual) * 100
            else:
                pct_conclusao_atual = 1.0
                pct_texto_atual = 100.0
            st.progress(pct_conclusao_atual, text=f"🎯 Progresso Meta Corrente Ajustada: {pct_texto_atual:.1f}%")
            
            # --- BARRA 2: META ORIGINAL FIXA (SEM HISTÓRICO DE ERROS - EX: OS R$ 58.706 LIMPOS) ---
            if meta_individual_original_estatica > 0:
                pct_conclusao_orig = min(vendas_azul_con / meta_individual_original_estatica, 1.0)
                pct_texto_orig = (vendas_azul_con / meta_individual_original_estatica) * 100
            else:
                pct_conclusao_orig = 1.0
                pct_texto_orig = 100.0
            st.progress(pct_conclusao_orig, text=f"🏳️ Progresso Ref. Meta Original Limpa: {pct_texto_orig:.1f}%")
            
            st.markdown(" ") # Espaçamento entre as barras e os avisos
            
            valor_em_falta = meta_individual_semana_atual - vendas_azul_con
            if valor_em_falta > 0:
                st.warning(f"📉 **Falta para bater a meta ajustada:** R$ {valor_em_falta:,.2f}")
            else:
                st.success("🎉 **Meta Cumprida nesta semana!**")
            
            st.metric(label="Faturado na Azul", value=f"R$ {vendas_azul_con:,.2f}")
            st.caption(f"Ref. Alvo Original Fixo da Semana: R$ {meta_individual_original_estatica:,.2f}")
            st.caption(f"Vendas Fora da Azul: R$ {vendas_geral_con:,.2f}")
            st.markdown("---")

    st.markdown("**Comparativo Individual da Semana (Barras)**")
    if not df_da_semana.empty:
        df_barras_dados = df_da_semana.groupby("Participante")[["Vendas Azul", "Vendas Geral"]].sum()
        st.bar_chart(df_barras_dados)
    else:
        st.info("Sem lançamentos nesta semana.")


# ==================== ABA 2: RAIO-X DO QUADRIMESTRE ====================
with aba_quadrimestre:
    st.markdown("### 🔍 Análise Consolidada do Período Inteiro")
    df_acumulado = df_vendas_quad.groupby("Participante")[["Vendas Azul", "Vendas Geral"]].sum()
    
    if not df_acumulado.empty:
        st.markdown("**📊 Torre de Faturamento: Azul vs Fora da Azul (Acumulado do Período)**")
        st.bar_chart(df_acumulado, stack=True)
        st.markdown("---")
        
        st.markdown("**📋 Tabela de Faturação Acumulada do Quadrimestre**")
        df_resumo_total = df_acumulado.reset_index()
        df_resumo_total["Total Combinado"] = df_resumo_total["Vendas Azul"] + df_resumo_total["Vendas Geral"]
        
        df_tabela_visual = df_resumo_total.copy()
        df_tabela_visual["Vendas Azul"] = df_tabela_visual["Vendas Azul"].map("R$ {:,.2f}".format)
        df_tabela_visual["Vendas Geral"] = df_tabela_visual["Vendas Geral"].map("R$ {:,.2f}".format)
        df_tabela_visual["Total Combinado"] = df_tabela_visual["Total Combinado"].map("R$ {:,.2f}".format)
        st.dataframe(df_tabela_visual, use_container_width=True)
    else:
        st.info("Insira dados para habilitar a torre de faturamento.")

    st.markdown("---")
    st.markdown("**📈 Curva de Desempenho Semanal da Agência**")
    historico_linha = []
    for sem in semanas_lista:
        vendas_sem = df_vendas_quad[df_vendas_quad["Semana"] == sem]["Vendas Azul"].sum()
        meta_sem = metas_semanais_calculadas.get(sem, meta_base_pura_semana)
        if sem in df_vendas_quad["Semana"].unique():
            historico_linha.append({"Semana": sem, "Realizado Azul": vendas_sem, "Meta Exigida": meta_sem})
            
    if historico_linha:
        df_linha = pd.DataFrame(historico_linha).set_index("Semana")
        st.line_chart(df_linha)

st.markdown("---")
st.subheader("📋 Auditoria Geral de Bilhetes Cadastrados")
if not df_vendas_quad.empty:
    df_exibicao = df_vendas_quad.copy()
    df_exibicao["Total Bilhete"] = df_exibicao["Vendas Azul"] + df_exibicao["Vendas Geral"]
    st.dataframe(df_exibicao[["Semana", "Participante", "Localizador", "Vendas Azul", "Vendas Geral", "Total Bilhete"]], use_container_width=True)