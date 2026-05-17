import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Gestão de Metas Quadrimestrais", layout="wide")
st.title("✈️ Sistema Integrado de Metas e Localizadores - Azul")

# 2. CONEXÃO DIRETA COM O GOOGLE SHEETS
# O Streamlit busca as credenciais secretas (Secrets) automaticamente por trás das cenas
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para carregar dados em tempo real da nuvem (Forçando o Link Novo)
# Versão blindada para evitar quebras por cache ou abas ausentes
def carregar_dados_nuvem():
    # Coloque o novo link limpo aqui dentro
    url_sheets = "https://docs.google.com/spreadsheets/d/1ua3qaHvOR5c6HYXKlCKO4MyKPOyKMaIoy0McnyZQ55c/edit"
    try:
        df_v_nuvem = conn.read(spreadsheet=url_sheets, worksheet="vendas", ttl="0m")
        df_e_nuvem = conn.read(spreadsheet=url_sheets, worksheet="equipa_consultores", ttl="0m")
        return df_v_nuvem, df_e_nuvem
    except Exception as e:
        st.error("⚠️ Erro na conexão! Verifique se as abas 'vendas' e 'equipa_consultores' existem na planilha e se o e-mail da Conta de Serviço está adicionado como Editor.")
        st.info(f"Detalhes técnicos para auditoria: {str(e)}")
        st.stop()

# Ler os dados vindos diretamente da sua planilha online
df_vendas, df_equipa = carregar_dados_nuvem()

# Transformar a coluna da equipa numa lista para os menus selectbox
lista_consultores = df_equipa["Nome"].dropna().tolist()

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

# 4. PAINEL LATERAL: CADASTRAR CONSULTOR (GRAVAÇÃO DIRETA NA NUVEM)
st.sidebar.markdown("---")
with st.sidebar.expander("👤 Cadastrar Novo Colaborador"):
    novo_consultor = st.text_input("Nome do Novo Consultor:").strip()
    if st.button("Adicionar à Equipa"):
        if novo_consultor and novo_consultor not in lista_consultores:
            # Criar nova linha e juntar à tabela atual da equipa
            nova_equipa = pd.concat([df_equipa, pd.DataFrame({"Nome": [novo_consultor]})], ignore_index=True)
            # Atualizar a folha específica no Google Sheets
            conn.update(worksheet="equipa_consultores", data=nova_equipa)
            st.success(f"✅ {novo_consultor} salvo no Google Sheets!")
            st.rerun()

# 5. PAINEL LATERAL: LANÇAMENTO DE VENDAS (GRAVAÇÃO DIRETA NA NUVEM)
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
    localizador_existe = df_vendas["Localizador"].astype(str).str.upper() == localizador_sel if not df_vendas.empty else pd.Series([False])
    
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
        # Unir ao histórico online e enviar para a nuvem
        df_atualizado = pd.concat([df_vendas, pd.DataFrame([nova_venda_dict])], ignore_index=True)
        conn.update(worksheet="vendas", data=df_atualizado)
        st.sidebar.success("✅ Venda integrada e salva no Google Sheets!")
        st.rerun()

# Filtrar vendas do quadrimestre selecionado
df_vendas_quad = df_vendas[df_vendas["Quadrimestre"] == quadrimestre_ativo] if not df_vendas.empty else pd.DataFrame(columns=df_vendas.columns)

# 6. CÁLCULO DAS METAS ROLANTES SEMANAIS COLETIVAS
metas_semanais_calculadas = {}
acumulado_deficit_geral = 0.0

for sem in semanas_lista:
    meta_base_agencia_semana = meta_base_pura_semana + acumulado_deficit_geral
    metas_semanais_calculadas[sem] = max(meta_base_agencia_semana, 0.0)
    
    vendas_reais_semana = df_vendas_quad[df_vendas_quad["Semana"] == sem]["Vendas Azul"].sum() if not df_vendas_quad.empty else 0.0
    acumulado_deficit_geral = meta_base_agencia_semana - vendas_reais_semana

# 7. INDICADORES DO TOPO
st.subheader(f"📅 Monitorização: {quadrimestre_ativo}")
total_azul_quad_atual = df_vendas_quad["Vendas Azul"].sum() if not df_vendas_quad.empty else 0.0
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
    meta_individual_semana_atual = meta_coletiva_semana_atual / len(lista_consultores) if len(lista_consultores) > 0 else 0.0
    meta_individual_original_estatica = meta_base_pura_semana / len(lista_consultores) if len(lista_consultores) > 0 else 0.0

    df_da_semana = df_vendas_quad[df_vendas_quad["Semana"] == semana_visualizar] if not df_vendas_quad.empty else pd.DataFrame()
    total_azul_sem = df_da_semana["Vendas Azul"].sum() if not df_da_semana.empty else 0.0
    total_geral_sem = df_da_semana["Vendas Geral"].sum() if not df_da_semana.empty else 0.0

    st.markdown(f"#### 📈 Desempenho — {semana_visualizar}")
    st.markdown(f"**Meta Geral Corrente (Com Reajuste):** R$ {meta_coletiva_semana_atual:,.2f} | **Meta Alvo Original Limpa:** R$ {meta_base_pura_semana:,.2f}")
    
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

    st.markdown("##### 👥 Situação Atualizada por Consultor")
    if len(lista_consultores) > 0:
        colunas_consultores = st.columns(len(lista_consultores))
        for idx, consultor in enumerate(lista_consultores):
            vendas_azul_con = df_da_semana[df_da_semana["Participante"] == consultor]["Vendas Azul"].sum() if not df_da_semana.empty else 0.0
            vendas_geral_con = df_da_semana[df_da_semana["Participante"] == consultor]["Vendas Geral"].sum() if not df_da_semana.empty else 0.0
            
            with colunas_consultores[idx]:
                st.markdown(f"### 👤 {consultor}")
                
                # Barra Meta Corrente
                if meta_individual_semana_atual > 0:
                    pct_c_atual = min(vendas_azul_con / meta_individual_semana_atual, 1.0)
                    pct_t_atual = (vendas_azul_con / meta_individual_semana_atual) * 100
                else:
                    pct_c_atual, pct_t_atual = 1.0, 100.0
                st.progress(pct_c_atual, text=f"🎯 Meta Ajustada: {pct_t_atual:.1f}%")
                
                # Barra Meta Original
                if meta_individual_original_estatica > 0:
                    pct_c_orig = min(vendas_azul_con / meta_individual_original_estatica, 1.0)
                    pct_t_orig = (vendas_azul_con / meta_individual_original_estatica) * 100
                else:
                    pct_c_orig, pct_t_orig = 1.0, 100.0
                st.progress(pct_c_orig, text=f"🏳️ Meta Original: {pct_t_orig:.1f}%")
                
                st.markdown(" ")
                valor_em_falta = meta_individual_semana_atual - vendas_azul_con
                if valor_em_falta > 0:
                    st.warning(f"📉 **Falta:** R$ {valor_em_falta:,.2f}")
                else:
                    st.success("🎉 **Meta Batida!**")
                
                st.metric(label="Faturado na Azul", value=f"R$ {vendas_azul_con:,.2f}")
                st.caption(f"Ref. Alvo Fixo: R$ {meta_individual_original_estatica:,.2f}")
                st.caption(f"Fora da Azul: R$ {vendas_geral_con:,.2f}")
                st.markdown("---")
    else:
        st.info("Nenhum consultor cadastrado na planilha.")

    st.markdown("**Comparativo Individual da Semana (Barras)**")
    if not df_da_semana.empty:
        df_barras_dados = df_da_semana.groupby("Participante")[["Vendas Azul", "Vendas Geral"]].sum()
        st.bar_chart(df_barras_dados)
    else:
        st.info("Sem lançamentos nesta semana.")

# ==================== ABA 2: RAIO-X DO QUADRIMESTRE ====================
with aba_quadrimestre:
    st.markdown("### 🔍 Análise Consolidada do Período Inteiro")
    if not df_vendas_quad.empty:
        df_acumulado = df_vendas_quad.groupby("Participante")[["Vendas Azul", "Vendas Geral"]].sum()
        st.markdown("**📊 Torre de Faturamento: Azul vs Fora da Azul**")
        st.bar_chart(df_acumulado, stack=True)
        st.markdown("---")
        
        st.markdown("**📋 Tabela de Faturação Acumulada**")
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
        if not df_vendas_quad.empty and sem in df_vendas_quad["Semana"].unique():
            vendas_sem = df_vendas_quad[df_vendas_quad["Semana"] == sem]["Vendas Azul"].sum()
            meta_sem = metas_semanais_calculadas.get(sem, meta_base_pura_semana)
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
