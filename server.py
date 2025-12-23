import threading
import asyncio
import time
import os
import random
import aiohttp
import ssl
import urllib3
import json
import traceback
import requests
import base64
import zipfile
import io
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string, session, abort, send_file, redirect, url_for

# --- PERSISTÊNCIA AUTOMÁTICA EM JSON ---
def load_json(filename, default):
    if not os.path.exists(filename):
        with open(filename, 'w') as f: json.dump(default, f, indent=4)
        return default
    try:
        with open(filename, 'r') as f: return json.load(f)
    except: return default

def save_json(filename, data):
    with open(filename, 'w') as f: json.dump(data, f, indent=4)

CONFIG_FILE = "thayson_config.json"
BANS_FILE = "thayson_bans.json"
ACCOUNTS_FILE = "contas.json" # Novo arquivo de persistência de usuários

# Inicializa dados
default_conf = {"app_password": "123", "admin_password": "admin thayson"}
ADMIN_CONFIG_DB = load_json(CONFIG_FILE, default_conf)
BANNED_DB = load_json(BANS_FILE, {})
USER_DB = load_json(ACCOUNTS_FILE, {}) # { "nome": {"ip": "", "last_login": ""} }

ADMIN_CONFIG = {
    "active_users": {}, 
    "logs": []
}

# Evento Global de Controle de Spam
STOP_SPAM_EVENT = threading.Event()

# --- Importações Originais ---
try:
    from Crypto.Cipher import AES 
    from Crypto.Util.Padding import pad, unpad
    from byte import encrypt_api, Encrypt_ID
    from packet import DecodeHex, EncryptPacket, PlayerStatus, SwitchLoneWolf, SwitchLoneWolfDule, InvitePlayer, StartGame, GlitchFixKick, LeaveTeam, CreateProtobufPacket, DecodeProtobufPacket 
    from Pb2 import MajorLogin_pb2, GetLoginData_pb2
except ImportError:
    class PlaceholderModule:
        def __getattr__(self, name): return None
    globals()['AES'] = PlaceholderModule()
    globals()['pad'] = lambda data, block_size: data
    globals()['unpad'] = lambda data, block_size: data
    pass 
    
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================================
# 🛠️ TODAS AS CONTAS (100% MANTIDO - SEM CORTES)
# ===============================================

FF_ACCOUNTS_BR = {
    "BOT_01": ["4348309109", "likes_O79P6_BY_SPIDEERIO_GAMING_G1Q4P", "https://loginbp.ggpolarbear.com"],
    "BOT_02": ["4348309105", "likes_4I8MY_BY_SPIDEERIO_GAMING_QFLH2", "https://loginbp.ggpolarbear.com"],
    "BOT_03": ["4348309107", "likes_MDY46_BY_SPIDEERIO_GAMING_GCNBG", "https://loginbp.ggpolarbear.com"],
    "BOT_04": ["4348309110", "likes_GMWWR_BY_SPIDEERIO_GAMING_9T6J1", "https://loginbp.ggpolarbear.com"],
    "BOT_05": ["4348309106", "likes_J86BK_BY_SPIDEERIO_GAMING_QO38T", "https://loginbp.ggpolarbear.com"],
    "BOT_06": ["4348309113", "likes_E66R5_BY_SPIDEERIO_GAMING_9Z3TK", "https://loginbp.ggpolarbear.com"],
    "BOT_07": ["4348309112", "likes_Z2I4N_BY_SPIDEERIO_GAMING_9D08L", "https://loginbp.ggpolarbear.com"],
    "BOT_08": ["4348311081", "likes_JKTHD_BY_SPIDEERIO_GAMING_KA4TX", "https://loginbp.ggpolarbear.com"],
    "BOT_09": ["4348309108", "likes_8VW43_BY_SPIDEERIO_GAMING_APYYX", "https://loginbp.ggpolarbear.com"],
    "BOT_10": ["4348309104", "likes_PVZCT_BY_SPIDEERIO_GAMING_9MIO8", "https://loginbp.ggpolarbear.com"],
    "BOT_11": ["4348309225", "likes_PAV4S_BY_SPIDEERIO_GAMING_H8QPU", "https://loginbp.ggpolarbear.com"],
    "BOT_12": ["4348309223", "likes_WI1N5_BY_SPIDEERIO_GAMING_MG2S9", "https://loginbp.ggpolarbear.com"],
    "BOT_13": ["4348309230", "likes_U0UGS_BY_SPIDEERIO_GAMING_IUAD7", "https://loginbp.ggpolarbear.com"],
    "BOT_14": ["4348309243", "likes_OMH22_BY_SPIDEERIO_GAMING_8OIV6", "https://loginbp.ggpolarbear.com"],
    "BOT_15": ["4348309236", "likes_E8Z07_BY_SPIDEERIO_GAMING_BS3WG", "https://loginbp.ggpolarbear.com"],
    "BOT_16": ["4348309237", "likes_6VATQ_BY_SPIDEERIO_GAMING_I2SC7", "https://loginbp.ggpolarbear.com"],
    "BOT_17": ["4348309249", "likes_GT2TM_BY_SPIDEERIO_GAMING_ZZCL1", "https://loginbp.ggpolarbear.com"],
    "BOT_18": ["4348309248", "likes_SW5YQ_BY_SPIDEERIO_GAMING_9H06F", "https://loginbp.ggpolarbear.com"],
    "BOT_19": ["4348309222", "likes_OKGHH_BY_SPIDEERIO_GAMING_55WS8", "https://loginbp.ggpolarbear.com"],
    "BOT_20": ["4348309310", "likes_71PDH_BY_SPIDEERIO_GAMING_URW3K", "https://loginbp.ggpolarbear.com"],
    "BOT_21": ["4348309447", "likes_CIDV5_BY_SPIDEERIO_GAMING_W7BH6", "https://loginbp.ggpolarbear.com"],
    "BOT_22": ["4348309445", "likes_81EHB_BY_SPIDEERIO_GAMING_NS25Q", "https://loginbp.ggpolarbear.com"],
    "BOT_23": ["4348309454", "likes_RHC9O_BY_SPIDEERIO_GAMING_SMTOD", "https://loginbp.ggpolarbear.com"],
    "BOT_24": ["4348309441", "likes_X1GI0_BY_SPIDEERIO_GAMING_S2SUM", "https://loginbp.ggpolarbear.com"],
    "BOT_25": ["4348309452", "likes_A4HZB_BY_SPIDEERIO_GAMING_YUCC1", "https://loginbp.ggpolarbear.com"],
    "BOT_26": ["4348309472", "likes_ZYDH5_BY_SPIDEERIO_GAMING_HCKVF", "https://loginbp.ggpolarbear.com"],
    "BOT_27": ["4348309457", "likes_FD2OK_BY_SPIDEERIO_GAMING_JDW9E", "https://loginbp.ggpolarbear.com"],
    "BOT_28": ["4348309462", "likes_VGGS3_BY_SPIDEERIO_GAMING_6ROTY", "https://loginbp.ggpolarbear.com"],
    "BOT_29": ["4348309471", "likes_MXN8C_BY_SPIDEERIO_GAMING_1WWDF", "https://loginbp.ggpolarbear.com"],
    "BOT_30": ["4348309510", "likes_OUI65_BY_SPIDEERIO_GAMING_F1WW0", "https://loginbp.ggpolarbear.com"],
    "BOT_31": ["4348309584", "likes_53I5J_BY_SPIDEERIO_GAMING_QMI54", "https://loginbp.ggpolarbear.com"],
    "BOT_32": ["4348309588", "likes_UPUQS_BY_SPIDEERIO_GAMING_9NN21", "https://loginbp.ggpolarbear.com"],
    "BOT_33": ["4348309587", "likes_H5GFK_BY_SPIDEERIO_GAMING_UKMJP", "https://loginbp.ggpolarbear.com"],
    "BOT_34": ["4348309595", "likes_J31HM_BY_SPIDEERIO_GAMING_2QOQG", "https://loginbp.ggpolarbear.com"],
    "BOT_35": ["4348309589", "likes_L0A0Y_BY_SPIDEERIO_GAMING_UEDJG", "https://loginbp.ggpolarbear.com"],
    "BOT_36": ["4348309605", "likes_FZO9N_BY_SPIDEERIO_GAMING_X30JY", "https://loginbp.ggpolarbear.com"],
    "BOT_37": ["4348309601", "likes_LFX0R_BY_SPIDEERIO_GAMING_BDCW8", "https://loginbp.ggpolarbear.com"],
    "BOT_38": ["4348309603", "likes_V84FZ_BY_SPIDEERIO_GAMING_DKDJ7", "https://loginbp.ggpolarbear.com"],
    "BOT_39": ["4348309614", "likes_VOLY7_BY_SPIDEERIO_GAMING_Y0IDA", "https://loginbp.ggpolarbear.com"],
    "BOT_40": ["4348311083", "likes_CN6P3_BY_SPIDEERIO_GAMING_YVN39", "https://loginbp.ggpolarbear.com"],
    "BOT_41": ["4348311085", "likes_32G1D_BY_SPIDEERIO_GAMING_KAAKN", "https://loginbp.ggpolarbear.com"],
    "BOT_42": ["4348311079", "likes_ESA7K_BY_SPIDEERIO_GAMING_B86QM", "https://loginbp.ggpolarbear.com"],
    "BOT_43": ["4348311086", "likes_VT56D_BY_SPIDEERIO_GAMING_CZP36", "https://loginbp.ggpolarbear.com"],
    "BOT_44": ["4348311080", "likes_GBWSV_BY_SPIDEERIO_GAMING_9JSGM", "https://loginbp.ggpolarbear.com"],
    "BOT_45": ["4348311084", "likes_HTCFG_BY_SPIDEERIO_GAMING_H4Y1O", "https://loginbp.ggpolarbear.com"],
    "BOT_46": ["4348311078", "likes_Z5B16_BY_SPIDEERIO_GAMING_O88BE", "https://loginbp.ggpolarbear.com"],
    "BOT_47": ["4348311082", "likes_QAK05_BY_SPIDEERIO_GAMING_C9VFB", "https://loginbp.ggpolarbear.com"],
    "BOT_48": ["4348311081", "likes_JKTHD_BY_SPIDEERIO_GAMING_KA4TX", "https://loginbp.ggpolarbear.com"],
    "BOT_49": ["4348311087", "likes_RSLZR_BY_SPIDEERIO_GAMING_FONAE", "https://loginbp.ggpolarbear.com"],
    "BOT_50": ["4348311254", "likes_QABG5_BY_SPIDEERIO_GAMING_L1IKI", "https://loginbp.ggpolarbear.com"],
    "BOT_51": ["4347719438", "Silva_7EDRF_BY_SPIDEERIO_GAMING_BS6BM", "https://loginbp.ggpolarbear.com"],
    "BOT_52": ["4347719446", "Silva_CEWXG_BY_SPIDEERIO_GAMING_4MJMX", "https://loginbp.ggpolarbear.com"],
    "BOT_53": ["4347719453", "Silva_19CXW_BY_SPIDEERIO_GAMING_029VW", "https://loginbp.ggpolarbear.com"],
    "BOT_54": ["4347719439", "Silva_9KD28_BY_SPIDEERIO_GAMING_FNY1T", "https://loginbp.ggpolarbear.com"],
    "BOT_55": ["4347719437", "Silva_NEXCG_BY_SPIDEERIO_GAMING_P5D55", "https://loginbp.ggpolarbear.com"],
    "BOT_56": ["4347719738", "Silva_ENVP0_BY_SPIDEERIO_GAMING_YLNUR", "https://loginbp.ggpolarbear.com"],
    "BOT_57": ["4347719736", "Silva_4UKQO_BY_SPIDEERIO_GAMING_MRBUW", "https://loginbp.ggpolarbear.com"],
    "BOT_58": ["4347719734", "Silva_HDED5_BY_SPIDEERIO_GAMING_BTH08", "https://loginbp.ggpolarbear.com"],
    "BOT_59": ["4347719732", "Silva_B9T1S_BY_SPIDEERIO_GAMING_LWJG5", "https://loginbp.ggpolarbear.com"],
    "BOT_60": ["4347719741", "Silva_WLHZF_BY_SPIDEERIO_GAMING_CSZ33", "https://loginbp.ggpolarbear.com"],
    "BOT_61": ["4347719438", "Silva_7EDRF_BY_SPIDEERIO_GAMING_BS6BM", "https://loginbp.ggpolarbear.com"],
    "BOT_62": ["4347719446", "Silva_CEWXG_BY_SPIDEERIO_GAMING_4MJMX", "https://loginbp.ggpolarbear.com"],
    "BOT_63": ["4347719453", "Silva_19CXW_BY_SPIDEERIO_GAMING_029VW", "https://loginbp.ggpolarbear.com"],
    "BOT_64": ["4347719439", "Silva_9KD28_BY_SPIDEERIO_GAMING_FNY1T", "https://loginbp.ggpolarbear.com"],
    "BOT_65": ["4347719437", "Silva_NEXCG_BY_SPIDEERIO_GAMING_P5D55", "https://loginbp.ggpolarbear.com"],
    "BOT_66": ["4347719738", "Silva_ENVP0_BY_SPIDEERIO_GAMING_YLNUR", "https://loginbp.ggpolarbear.com"],
    "BOT_67": ["4347719736", "Silva_4UKQO_BY_SPIDEERIO_GAMING_MRBUW", "https://loginbp.ggpolarbear.com"],
    "BOT_68": ["4347719734", "Silva_HDED5_BY_SPIDEERIO_GAMING_BTH08", "https://loginbp.ggpolarbear.com"],
    "BOT_69": ["4347719732", "Silva_B9T1S_BY_SPIDEERIO_GAMING_LWJG5", "https://loginbp.ggpolarbear.com"],
    "BOT_70": ["4347719741", "Silva_WLHZF_BY_SPIDEERIO_GAMING_CSZ33", "https://loginbp.ggpolarbear.com"],
    "BOT_71": ["4348456850", "Likes_4A259_BY_SPIDEERIO_GAMING_HRKMG", "https://loginbp.ggpolarbear.com"],
    "BOT_72": ["4348456849", "Likes_MYSNF_BY_SPIDEERIO_GAMING_JPT69", "https://loginbp.ggpolarbear.com"],
    "BOT_73": ["4348456852", "Likes_181ZK_BY_SPIDEERIO_GAMING_I5IJ2", "https://loginbp.ggpolarbear.com"],
    "BOT_74": ["4348456851", "Likes_GHVQP_BY_SPIDEERIO_GAMING_1JDG8", "https://loginbp.ggpolarbear.com"],
    "BOT_75": ["4348456858", "Likes_T8DWI_BY_SPIDEERIO_GAMING_7PYZF", "https://loginbp.ggpolarbear.com"],
    "BOT_76": ["4348457050", "Likes_43ROM_BY_SPIDEERIO_GAMING_17VYF", "https://loginbp.ggpolarbear.com"],
    "BOT_77": ["4348457052", "Likes_PNBK2_BY_SPIDEERIO_GAMING_J8P4E", "https://loginbp.ggpolarbear.com"],
    "BOT_78": ["4348457056", "Likes_TBB2P_BY_SPIDEERIO_GAMING_EZWVK", "https://loginbp.ggpolarbear.com"],
    "BOT_79": ["4348457058", "Likes_KDQ34_BY_SPIDEERIO_GAMING_7XZGM", "https://loginbp.ggpolarbear.com"],
    "BOT_80": ["4348457067", "Likes_1OURK_BY_SPIDEERIO_GAMING_3RIQB", "https://loginbp.ggpolarbear.com"],
    "BOT_81": ["4348457227", "Likes_6X08T_BY_SPIDEERIO_GAMING_G8C7S", "https://loginbp.ggpolarbear.com"],
    "BOT_82": ["4348457223", "Likes_AA7ZT_BY_SPIDEERIO_GAMING_5RLHW", "https://loginbp.ggpolarbear.com"],
    "BOT_83": ["4348457231", "Likes_1D3P3_BY_SPIDEERIO_GAMING_2H3B6", "https://loginbp.ggpolarbear.com"],
    "BOT_84": ["4348457233", "Likes_TDV7S_BY_SPIDEERIO_GAMING_FRCZK", "https://loginbp.ggpolarbear.com"],
    "BOT_85": ["4348457230", "Likes_0T1Z1_BY_SPIDEERIO_GAMING_HO1AS", "https://loginbp.ggpolarbear.com"],
    "BOT_86": ["4348458613", "Likes_6FVR6_BY_SPIDEERIO_GAMING_YSJ8L", "https://loginbp.ggpolarbear.com"],
    "BOT_87": ["4348458622", "Likes_GQMB3_BY_SPIDEERIO_GAMING_USJBG", "https://loginbp.ggpolarbear.com"],
    "BOT_88": ["4348459312", "Likes_3BXLE_BY_SPIDEERIO_GAMING_HJOIK", "https://loginbp.ggpolarbear.com"],
    "BOT_89": ["4348459317", "Likes_U2CJX_BY_SPIDEERIO_GAMING_V4AN5", "https://loginbp.ggpolarbear.com"],
    "BOT_90": ["4348459335", "Likes_P9H2G_BY_SPIDEERIO_GAMING_6WFFW", "https://loginbp.ggpolarbear.com"],
    "BOT_91": ["4348459360", "Likes_4AWM0_BY_SPIDEERIO_GAMING_Y68CU", "https://loginbp.ggpolarbear.com"],
    "BOT_92": ["4348459394", "Likes_PRJB4_BY_SPIDEERIO_GAMING_LLH64", "https://loginbp.ggpolarbear.com"],
    "BOT_93": ["4348459574", "Likes_4W61A_BY_SPIDEERIO_GAMING_3M3TM", "https://loginbp.ggpolarbear.com"],
    "BOT_94": ["4348459575", "Likes_VCY1Y_BY_SPIDEERIO_GAMING_DXJFY", "https://loginbp.ggpolarbear.com"],
    "BOT_95": ["4348459596", "Likes_GWOR7_BY_SPIDEERIO_GAMING_V2R8A", "https://loginbp.ggpolarbear.com"],
    "BOT_96": ["4348459610", "Likes_P0XYM_BY_SPIDEERIO_GAMING_7F73G", "https://loginbp.ggpolarbear.com"],
    "BOT_97": ["4348459623", "Likes_UWK5Y_BY_SPIDEERIO_GAMING_D89L4", "https://loginbp.ggpolarbear.com"],
    "BOT_98": ["4348459764", "Likes_4BXM4_BY_SPIDEERIO_GAMING_ND6L5", "https://loginbp.ggpolarbear.com"],
    "BOT_99": ["4348459765", "Likes_V74Y4_BY_SPIDEERIO_GAMING_4F831", "https://loginbp.ggpolarbear.com"],
    "BOT_100": ["4348459774", "Likes_GLK6D_BY_SPIDEERIO_GAMING_AMARI", "https://loginbp.ggpolarbear.com"],
    "BOT_101": ["4348459790", "Likes_52OOU_BY_SPIDEERIO_GAMING_0SHME", "https://loginbp.ggpolarbear.com"],
    "BOT_102": ["4348459812", "Likes_6EBV0_BY_SPIDEERIO_GAMING_9XTPB", "https://loginbp.ggpolarbear.com"],
    "BOT_103": ["4348459935", "Likes_GAYFL_BY_SPIDEERIO_GAMING_QYUPP", "https://loginbp.ggpolarbear.com"],
    "BOT_104": ["4348459946", "Likes_O7FSI_BY_SPIDEERIO_GAMING_KNM8Y", "https://loginbp.ggpolarbear.com"],
    "BOT_105": ["4348459947", "Likes_ANNTR_BY_SPIDEERIO_GAMING_N8LZE", "https://loginbp.ggpolarbear.com"],
    "BOT_106": ["4348459963", "Likes_3OC7V_BY_SPIDEERIO_GAMING_LXKFI", "https://loginbp.ggpolarbear.com"],
    "BOT_107": ["4348459979", "Likes_9Z8KX_BY_SPIDEERIO_GAMING_PD9X8", "https://loginbp.ggpolarbear.com"],
    "BOT_108": ["4348460674", "Likes_BRTK0_BY_SPIDEERIO_GAMING_BO4D5", "https://loginbp.ggpolarbear.com"],
    "BOT_109": ["4348460687", "Likes_W37J8_BY_SPIDEERIO_GAMING_B9WMP", "https://loginbp.ggpolarbear.com"],
    "BOT_110": ["4348460714", "Likes_Q1F2G_BY_SPIDEERIO_GAMING_UBMOU", "https://loginbp.ggpolarbear.com"],
    "BOT_111": ["4348460712", "Likes_YPI4A_BY_SPIDEERIO_GAMING_U4H8Z", "https://loginbp.ggpolarbear.com"],
    "BOT_112": ["4348460751", "Likes_5E3L4_BY_SPIDEERIO_GAMING_36TH7", "https://loginbp.ggpolarbear.com"],
    "BOT_113": ["4348460956", "Likes_9PV49_BY_SPIDEERIO_GAMING_6X81U", "https://loginbp.ggpolarbear.com"],
    "BOT_114": ["4348460957", "Likes_FZINB_BY_SPIDEERIO_GAMING_STLLV", "https://loginbp.ggpolarbear.com"],
    "BOT_115": ["4348460974", "Likes_QQIMZ_BY_SPIDEERIO_GAMING_ZBJLP", "https://loginbp.ggpolarbear.com"],
    "BOT_116": ["4348460997", "Likes_O111O_BY_SPIDEERIO_GAMING_IVY8W", "https://loginbp.ggpolarbear.com"],
    "BOT_117": ["4348461029", "Likes_87ROK_BY_SPIDEERIO_GAMING_AITXP", "https://loginbp.ggpolarbear.com"],
    "BOT_118": ["4348461124", "Likes_4SUNP_BY_SPIDEERIO_GAMING_0VJHY", "https://loginbp.ggpolarbear.com"],
    "BOT_119": ["4348461130", "Likes_3HUFS_BY_SPIDEERIO_GAMING_O5SKS", "https://loginbp.ggpolarbear.com"],
    "BOT_120": ["4348461139", "Likes_Y5Y9G_BY_SPIDEERIO_GAMING_52YPC", "https://loginbp.ggpolarbear.com"],
    "BOT_121": ["4348461154", "Likes_R4KCQ_BY_SPIDEERIO_GAMING_D6Z7H", "https://loginbp.ggpolarbear.com"],
    "BOT_122": ["4348461186", "Likes_GL5WI_BY_SPIDEERIO_GAMING_6O5W5", "https://loginbp.ggpolarbear.com"],
    "BOT_123": ["4348461308", "Likes_GNRRG_BY_SPIDEERIO_GAMING_3R533", "https://loginbp.ggpolarbear.com"],
    "BOT_124": ["4348461307", "Likes_6CQ0Z_BY_SPIDEERIO_GAMING_CYXJL", "https://loginbp.ggpolarbear.com"],
    "BOT_125": ["4348461330", "Likes_JCIT2_BY_SPIDEERIO_GAMING_RG2QV", "https://loginbp.ggpolarbear.com"],
    "BOT_126": ["4348461343", "Likes_LN1HR_BY_SPIDEERIO_GAMING_86VV3", "https://loginbp.ggpolarbear.com"],
    "BOT_127": ["4348461366", "Likes_5SKO7_BY_SPIDEERIO_GAMING_MLZU9", "https://loginbp.ggpolarbear.com"],
    "BOT_128": ["4357214742", "Visit_0M1V7_BY_SPIDEERIO_GAMING_X6BVQ", "https://loginbp.ggpolarbear.com"],
    "BOT_129": ["4357214740", "Visit_4P61T_BY_SPIDEERIO_GAMING_NDKGK", "https://loginbp.ggpolarbear.com"],
    "BOT_130": ["4357214741", "Visit_Y13BU_BY_SPIDEERIO_GAMING_WC83T", "https://loginbp.ggpolarbear.com"],
    "BOT_131": ["4357214743", "Visit_ACT9H_BY_SPIDEERIO_GAMING_AJJ5G", "https://loginbp.ggpolarbear.com"],
    "BOT_132": ["4357214744", "Visit_33CUA_BY_SPIDEERIO_GAMING_ABUPR", "https://loginbp.ggpolarbear.com"],
    "BOT_133": ["4357214902", "Visit_326W4_BY_SPIDEERIO_GAMING_19R87", "https://loginbp.ggpolarbear.com"],
    "BOT_134": ["4357214903", "Visit_WQ6DH_BY_SPIDEERIO_GAMING_HPIOG", "https://loginbp.ggpolarbear.com"],
    "BOT_135": ["4357214905", "Visit_HF65B_BY_SPIDEERIO_GAMING_30K9C", "https://loginbp.ggpolarbear.com"],
    "BOT_136": ["4357214904", "Visit_H2136_BY_SPIDEERIO_GAMING_ABCU5", "https://loginbp.ggpolarbear.com"],
    "BOT_137": ["4357214906", "Visit_QTGKH_BY_SPIDEERIO_GAMING_PNRBX", "https://loginbp.ggpolarbear.com"],
    "BOT_138": ["4357215054", "Visit_FYJBZ_BY_SPIDEERIO_GAMING_P0JI9", "https://loginbp.ggpolarbear.com"],
    "BOT_139": ["4357215053", "Visit_VHXVY_BY_SPIDEERIO_GAMING_S9S0Y", "https://loginbp.ggpolarbear.com"],
    "BOT_140": ["4357215042", "Visit_0MNO8_BY_SPIDEERIO_GAMING_HR346", "https://loginbp.ggpolarbear.com"],
    "BOT_141": ["4357215051", "Visit_X3QDE_BY_SPIDEERIO_GAMING_REM05", "https://loginbp.ggpolarbear.com"],
    "BOT_142": ["4357215050", "Visit_YGG4L_BY_SPIDEERIO_GAMING_2IM7A", "https://loginbp.ggpolarbear.com"],
    "BOT_143": ["4357215339", "Visit_5YE5T_BY_SPIDEERIO_GAMING_3PU7R", "https://loginbp.ggpolarbear.com"],
    "BOT_144": ["4357215309", "Visit_L4KYW_BY_SPIDEERIO_GAMING_ZXSPM", "https://loginbp.ggpolarbear.com"],
    "BOT_145": ["4357215493", "Visit_FJS5O_BY_SPIDEERIO_GAMING_BTFXL", "https://loginbp.ggpolarbear.com"],
    "BOT_146": ["4357215628", "Visit_HORV7_BY_SPIDEERIO_GAMING_WSUQR", "https://loginbp.ggpolarbear.com"],
    "BOT_147": ["4357215682", "Visit_W8VY8_BY_SPIDEERIO_GAMING_EOOQL", "https://loginbp.ggpolarbear.com"],
    "BOT_148": ["4357215663", "Visit_7ZC2P_BY_SPIDEERIO_GAMING_DJBWE", "https://loginbp.ggpolarbear.com"],
    "BOT_149": ["4357215928", "Visit_VW39D_BY_SPIDEERIO_GAMING_CWG84", "https://loginbp.ggpolarbear.com"],
    "BOT_150": ["4357215998", "Visit_30U4U_BY_SPIDEERIO_GAMING_R76KC", "https://loginbp.ggpolarbear.com"],
    "BOT_151": ["4357216021", "Visit_IIEAB_BY_SPIDEERIO_GAMING_N3FCS", "https://loginbp.ggpolarbear.com"],
    "BOT_152": ["4357216025", "Visit_QVP4M_BY_SPIDEERIO_GAMING_LMCDE", "https://loginbp.ggpolarbear.com"],
    "BOT_153": ["4357216045", "Visit_V54WF_BY_SPIDEERIO_GAMING_APAY6", "https://loginbp.ggpolarbear.com"],
    "BOT_154": ["4357216140", "Visit_UC2T4_BY_SPIDEERIO_GAMING_IA9NB", "https://loginbp.ggpolarbear.com"],
    "BOT_155": ["4357216144", "Visit_5G8SD_BY_SPIDEERIO_GAMING_RGMEC", "https://loginbp.ggpolarbear.com"],
    "BOT_156": ["4357216161", "Visit_1RSDJ_BY_SPIDEERIO_GAMING_T5KZ2", "https://loginbp.ggpolarbear.com"],
    "BOT_157": ["4357216158", "Visit_Q3BV2_BY_SPIDEERIO_GAMING_ZYYXO", "https://loginbp.ggpolarbear.com"],
    "BOT_158": ["4357216173", "Visit_9QR5X_BY_SPIDEERIO_GAMING_QUKXK", "https://loginbp.ggpolarbear.com"],
    "BOT_159": ["4357216248", "Visit_UDM8Q_BY_SPIDEERIO_GAMING_0Q06H", "https://loginbp.ggpolarbear.com"],
    "BOT_160": ["4357216253", "Visit_PNOY5_BY_SPIDEERIO_GAMING_RLOIT", "https://loginbp.ggpolarbear.com"],
    "BOT_161": ["4357216276", "Visit_SL08Q_BY_SPIDEERIO_GAMING_O33TL", "https://loginbp.ggpolarbear.com"],
    "BOT_162": ["4357216277", "Visit_G0OAK_BY_SPIDEERIO_GAMING_CXYP4", "https://loginbp.ggpolarbear.com"],
    "BOT_163": ["4357216299", "Visit_IK1RN_BY_SPIDEERIO_GAMING_96QUW", "https://loginbp.ggpolarbear.com"],
    "BOT_164": ["4357216363", "Visit_31XIN_BY_SPIDEERIO_GAMING_9XCCM", "https://loginbp.ggpolarbear.com"],
    "BOT_165": ["4357216374", "Visit_Z63C8_BY_SPIDEERIO_GAMING_YS2W3", "https://loginbp.ggpolarbear.com"],
    "BOT_166": ["4357216607", "Visit_RIA1A_BY_SPIDEERIO_GAMING_W3ZFU", "https://loginbp.ggpolarbear.com"],
    "BOT_167": ["4357216624", "Visit_0LAZG_BY_SPIDEERIO_GAMING_93M0V", "https://loginbp.ggpolarbear.com"],
    "BOT_168": ["4357216673", "Visit_FQ9NU_BY_SPIDEERIO_GAMING_XCAQT", "https://loginbp.ggpolarbear.com"],
    "BOT_169": ["4357216674", "Visit_7MBJG_BY_SPIDEERIO_GAMING_POBS1", "https://loginbp.ggpolarbear.com"],
    "BOT_170": ["4357216693", "Visit_GYQA4_BY_SPIDEERIO_GAMING_R739E", "https://loginbp.ggpolarbear.com"],
    "BOT_171": ["4357216800", "Visit_LXEDC_BY_SPIDEERIO_GAMING_20QJS", "https://loginbp.ggpolarbear.com"],
    "BOT_172": ["4357216805", "Visit_MBMH2_BY_SPIDEERIO_GAMING_GESXI", "https://loginbp.ggpolarbear.com"],
    "BOT_173": ["4357216835", "Visit_2D6MB_BY_SPIDEERIO_GAMING_VW6B4", "https://loginbp.ggpolarbear.com"],
    "BOT_174": ["4357216839", "Visit_B9SLY_BY_SPIDEERIO_GAMING_U8OLN", "https://loginbp.ggpolarbear.com"],
    "BOT_175": ["4357216848", "Visit_WH881_BY_SPIDEERIO_GAMING_R1HVC", "https://loginbp.ggpolarbear.com"],
    "BOT_176": ["4357216946", "Visit_JF8LJ_BY_SPIDEERIO_GAMING_ALBE8", "https://loginbp.ggpolarbear.com"],
    "BOT_177": ["4357216955", "Visit_6Z7IR_BY_SPIDEERIO_GAMING_110I7", "https://loginbp.ggpolarbear.com"],
    "BOT_178": ["4357216970", "Visit_V85IN_BY_SPIDEERIO_GAMING_5HCQV", "https://loginbp.ggpolarbear.com"],
    "BOT_179": ["4357216973", "Visit_JA6QA_BY_SPIDEERIO_GAMING_CV4A8", "https://loginbp.ggpolarbear.com"],
    "BOT_180": ["4357216986", "Visit_9EGMR_BY_SPIDEERIO_GAMING_ZFLKR", "https://loginbp.ggpolarbear.com"],
    "BOT_181": ["4357217089", "Visit_YCR0N_BY_SPIDEERIO_GAMING_6AAHS", "https://loginbp.ggpolarbear.com"],
    "BOT_182": ["4357217092", "Visit_3YLMS_BY_SPIDEERIO_GAMING_2ZV60", "https://loginbp.ggpolarbear.com"],
    "BOT_183": ["4357217103", "Visit_G7U8X_BY_SPIDEERIO_GAMING_V670B", "https://loginbp.ggpolarbear.com"],
    "BOT_184": ["4357217111", "Visit_MKE86_BY_SPIDEERIO_GAMING_Z9DCZ", "https://loginbp.ggpolarbear.com"],
    "BOT_185": ["4357217127", "Visit_XMA8U_BY_SPIDEERIO_GAMING_S8FLC", "https://loginbp.ggpolarbear.com"],
    "BOT_186": ["4357217629", "Visit_PHUTS_BY_SPIDEERIO_GAMING_8ZEEN", "https://loginbp.ggpolarbear.com"],
    "BOT_187": ["4357217632", "Visit_SKTA3_BY_SPIDEERIO_GAMING_O0YME", "https://loginbp.ggpolarbear.com"],
    "BOT_188": ["4357217637", "Visit_H616N_BY_SPIDEERIO_GAMING_RTLXF", "https://loginbp.ggpolarbear.com"],
    "BOT_189": ["4357217669", "Visit_XY5N1_BY_SPIDEERIO_GAMING_HMAKD", "https://loginbp.ggpolarbear.com"],
    "BOT_190": ["4357217666", "Visit_MADC2_BY_SPIDEERIO_GAMING_R9FDB", "https://loginbp.ggpolarbear.com"],
    "BOT_191": ["4357217820", "Visit_LS589_BY_SPIDEERIO_GAMING_RED71", "https://loginbp.ggpolarbear.com"],
    "BOT_192": ["4357217823", "Visit_4THPY_BY_SPIDEERIO_GAMING_31SRW", "https://loginbp.ggpolarbear.com"],
    "BOT_193": ["4357217829", "Visit_OT3DF_BY_SPIDEERIO_GAMING_A6L5D", "https://loginbp.ggpolarbear.com"],
    "BOT_194": ["4357217864", "Visit_KWDU9_BY_SPIDEERIO_GAMING_4GC2U", "https://loginbp.ggpolarbear.com"],
    "BOT_195": ["4357217866", "Visit_O43XD_BY_SPIDEERIO_GAMING_SU2V4", "https://loginbp.ggpolarbear.com"],
    "BOT_196": ["4357217964", "Visit_ZOD9T_BY_SPIDEERIO_GAMING_56BSI", "https://loginbp.ggpolarbear.com"],
    "BOT_197": ["4357217967", "Visit_RIB0W_BY_SPIDEERIO_GAMING_F2PTC", "https://loginbp.ggpolarbear.com"],
    "BOT_198": ["4357217972", "Visit_RLNID_BY_SPIDEERIO_GAMING_RKQX3", "https://loginbp.ggpolarbear.com"],
    "BOT_199": ["4357218007", "Visit_DFTEP_BY_SPIDEERIO_GAMING_JHR6T", "https://loginbp.ggpolarbear.com"],
    "BOT_200": ["4357218045", "Visit_QIEGX_BY_SPIDEERIO_GAMING_J45DH", "https://loginbp.ggpolarbear.com"],
    "BOT_201": ["4357218092", "Visit_83N0S_BY_SPIDEERIO_GAMING_B24XO", "https://loginbp.ggpolarbear.com"],
    "BOT_202": ["4357218093", "Visit_1MZTT_BY_SPIDEERIO_GAMING_88HB2", "https://loginbp.ggpolarbear.com"],
    "BOT_203": ["4357218103", "Visit_IUEJI_BY_SPIDEERIO_GAMING_F4QT8", "https://loginbp.ggpolarbear.com"],
    "BOT_204": ["4357218124", "Visit_XLJ7L_BY_SPIDEERIO_GAMING_JF7UW", "https://loginbp.ggpolarbear.com"],
    "BOT_205": ["4357218160", "Visit_L6R61_BY_SPIDEERIO_GAMING_0LGVQ", "https://loginbp.ggpolarbear.com"],
    "BOT_206": ["4357218652", "Visit_64KSF_BY_SPIDEERIO_GAMING_7CMMY", "https://loginbp.ggpolarbear.com"],
    "BOT_207": ["4357218674", "Visit_SCJ7K_BY_SPIDEERIO_GAMING_RYFNE", "https://loginbp.ggpolarbear.com"],
    "BOT_208": ["4357218681", "Visit_596GJ_BY_SPIDEERIO_GAMING_7Z2UW", "https://loginbp.ggpolarbear.com"],
    "BOT_209": ["4357218718", "Visit_JZYU6_BY_SPIDEERIO_GAMING_LMD32", "https://loginbp.ggpolarbear.com"],
    "BOT_210": ["4357218717", "Visit_3JJUQ_BY_SPIDEERIO_GAMING_WCH5G", "https://loginbp.ggpolarbear.com"],
    "BOT_211": ["4357218853", "Visit_8TG9X_BY_SPIDEERIO_GAMING_RN3ZC", "https://loginbp.ggpolarbear.com"],
    "BOT_212": ["4357218862", "Visit_MJM00_BY_SPIDEERIO_GAMING_JPNOL", "https://loginbp.ggpolarbear.com"],
    "BOT_213": ["4357218875", "Visit_C5PT9_BY_SPIDEERIO_GAMING_Y5E18", "https://loginbp.ggpolarbear.com"],
    "BOT_214": ["4357218901", "Visit_H6JML_BY_SPIDEERIO_GAMING_2VH8R", "https://loginbp.ggpolarbear.com"],
    "BOT_215": ["4357218903", "Visit_67R1B_BY_SPIDEERIO_GAMING_720SA", "https://loginbp.ggpolarbear.com"],
    "BOT_216": ["4357218991", "Visit_LSVBP_BY_SPIDEERIO_GAMING_C2XDU", "https://loginbp.ggpolarbear.com"],
    "BOT_217": ["4357219009", "Visit_YPMYE_BY_SPIDEERIO_GAMING_ZE829", "https://loginbp.ggpolarbear.com"],
    "BOT_218": ["4357219028", "Visit_MR28J_BY_SPIDEERIO_GAMING_J7HKB", "https://loginbp.ggpolarbear.com"],
    "BOT_219": ["4357219032", "Visit_2QJ8Y_BY_SPIDEERIO_GAMING_84QOH", "https://loginbp.ggpolarbear.com"],
    "BOT_220": ["4357219053", "Visit_62P55_BY_SPIDEERIO_GAMING_AESVI", "https://loginbp.ggpolarbear.com"],
    "BOT_221": ["4357219118", "Visit_TSNDD_BY_SPIDEERIO_GAMING_ZH0FB", "https://loginbp.ggpolarbear.com"],
    "BOT_222": ["4357219145", "Visit_LZCQR_BY_SPIDEERIO_GAMING_C8AE9", "https://loginbp.ggpolarbear.com"],
    "BOT_223": ["4357219163", "Visit_G9NYG_BY_SPIDEERIO_GAMING_R003Y", "https://loginbp.ggpolarbear.com"],
    "BOT_224": ["4357219174", "Visit_T5SA2_BY_SPIDEERIO_GAMING_4IFKS", "https://loginbp.ggpolarbear.com"],
    "BOT_225": ["4357219240", "Visit_263ZA_BY_SPIDEERIO_GAMING_KUH7L", "https://loginbp.ggpolarbear.com"],
    "BOT_226": ["4357219679", "Visit_MQLVK_BY_SPIDEERIO_GAMING_HWZV1", "https://loginbp.ggpolarbear.com"],
    "BOT_227": ["4357243432", "Visit_E0EBC_BY_SPIDEERIO_GAMING_JYE1X", "https://loginbp.ggpolarbear.com"],
    "BOT_228": ["4357243489", "Visit_RRTGF_BY_SPIDEERIO_GAMING_XO5OA", "https://loginbp.ggpolarbear.com"],
    "BOT_229": ["4357243403", "Visit_A9CW8_BY_SPIDEERIO_GAMING_5J83J", "https://loginbp.ggpolarbear.com"],
    "BOT_230": ["4357243435", "Visit_7BE1T_BY_SPIDEERIO_GAMING_MNYDP", "https://loginbp.ggpolarbear.com"],
}

REGIONS = { "BR": FF_ACCOUNTS_BR, "IND": {}, "US": {} }

# ===============================================
# 📊 CLASSES DE ESTADO (MANTIDAS)
# ===============================================

class Session:
    def __init__(self, bot_name, ff_uid):
        self.bot_name = bot_name
        self.is_running = False 
        self.ff_name = "NOME DESCONHECIDO"
        self.ff_uid = ff_uid
        self.ff_region = "???"
        self.ff_status_message = "OCIOSO"
        self.ff_total_games = 0 
        self.ff_target_uid = None   
        self.max_games = 0          
        self.current_session_games = 0 
        self.ff_kernel_task = None  
        self.ff_loop = None         
        self.invite_sent_time = None  
        self.invite_timeout_seconds = 60
        self._stop_event = threading.Event() 

class BotSessionManager:
    def __init__(self):
        self.sessions = { name: Session(name, config[0]) for name, config in FF_ACCOUNTS_BR.items() }
    def get_session(self, name): return self.sessions.get(name)

SESSION_MANAGER = BotSessionManager()
app = Flask(__name__)
app.secret_key = "thayson_master_key_4d_pro"

# ===============================================
# 🛡️ SEGURANÇA E PERSISTÊNCIA (CONTAS.JSON)
# ===============================================

@app.before_request
def security_check():
    ip = request.remote_addr
    
    # 1. Verifica Banimento (Se o IP estiver na lista e não expirou)
    if ip in BANNED_DB:
        info = BANNED_DB[ip]
        if info['expires'] == "PERMANENTE":
            return render_template_string(BAN_HTML, ip=ip, info=info)
        else:
            try:
                exp_date = datetime.strptime(info['expires'], "%Y-%m-%dT%H:%M")
                if datetime.now() < exp_date:
                    return render_template_string(BAN_HTML, ip=ip, info=info)
            except: pass

    # 2. Persistência de Login (Auto-login por IP)
    if 'user' not in session:
        for username, data in USER_DB.items():
            if data.get('ip') == ip:
                session['user'] = username
                break

    # 3. Proteção de Rotas (Redireciona se tentar entrar sem login)
    allowed_routes = ['home', 'auth_login', 'static', 'ban_zip', 'download_ban_report', 'stop_spam']
    if 'user' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404 NOT FOUND</h1><p>Acesso negado pelo Firewall Thayson.</p>", 404

# ===============================================
# 💎 INTERFACE HYPER-REALISTA (ESTILO 4D/LOVABLE)
# ===============================================

HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>THAYSON 4D | CONTROL</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap" rel="stylesheet">
    <style>
        body { background: #000; color: #fff; font-family: 'Orbitron', sans-serif; overflow-x: hidden; }
        #bg-canvas { position: fixed; top:0; left:0; z-index: -1; opacity: 0.6; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); border-radius: 40px; }
        .neon-border { border: 1px solid #00f2ff; box-shadow: 0 0 15px #00f2ff; }
        .btn-glow { background: linear-gradient(90deg, #00f2ff, #7000ff); transition: 0.4s; }
        .btn-glow:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0, 242, 255, 0.5); }
        .input-4d { background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.2); padding: 15px; border-radius: 20px; width: 100%; color: #00f2ff; outline: none; }
        .input-4d:focus { border-color: #00f2ff; box-shadow: 0 0 10px #00f2ff; }
    </style>
</head>
<body class="p-4">
    <canvas id="bg-canvas"></canvas>

    {% if page == 'login' %}
    <div class="flex items-center justify-center min-h-screen">
        <div class="glass p-12 max-w-md w-full text-center">
            <h1 class="text-4xl font-black mb-10 tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-600">THAYSON CORE</h1>
            <form action="/auth/login" method="POST" class="space-y-6">
                <input type="text" name="user" class="input-4d text-center" placeholder="IDENTIFIQUE-SE" required>
                <button class="btn-glow w-full py-5 rounded-3xl font-black uppercase">Estabelecer Conexão</button>
            </form>
        </div>
    </div>

    {% elif page == 'choice' %}
    <div class="flex flex-col items-center justify-center min-h-screen gap-10">
        <h2 class="text-3xl font-black text-cyan-400">SELECIONE A FREQUÊNCIA</h2>
        <div class="grid md:grid-cols-2 gap-8 w-full max-w-4xl px-4">
            <div class="glass p-16 text-center group cursor-pointer" onclick="checkPass('/panel')">
                <h3 class="text-2xl font-bold mb-4">PAINEL DO USUÁRIO</h3>
                <p class="text-xs text-gray-400">Acesso às funções de bot e likes massivos</p>
                <div class="mt-8 py-3 btn-glow rounded-2xl opacity-50 group-hover:opacity-100">ACESSAR</div>
            </div>
            <div class="glass p-16 text-center group cursor-pointer" onclick="checkPass('/admin')">
                <h3 class="text-2xl font-bold mb-4 text-purple-400">GRADE ADMIN</h3>
                <p class="text-xs text-gray-400">Configurações globais e segurança de rede</p>
                <div class="mt-8 py-3 bg-purple-600 rounded-2xl opacity-50 group-hover:opacity-100">MASTER</div>
            </div>
        </div>
    </div>

    {% elif page == 'panel' %}
    <div class="max-w-7xl mx-auto py-10">
        <div class="flex justify-between items-center mb-16 px-4">
            <h1 class="text-3xl font-black tracking-tighter">OPERAÇÕES_THAYSON <span class="text-cyan-400 text-sm">[ONLINE]</span></h1>
            <a href="/logout" class="text-red-500 font-bold border border-red-500 px-6 py-2 rounded-full hover:bg-red-500 hover:text-white transition">SAIR</a>
        </div>
        
        <div class="grid lg:grid-cols-3 gap-10 px-4">
            <div class="glass p-10 space-y-6">
                <h3 class="text-cyan-400 font-black">AÇÕES EM MASSA</h3>
                <input id="uid" placeholder="UID ALVO" class="input-4d">
                <button onclick="run('/like_all')" class="btn-glow w-full py-4 rounded-2xl font-bold">ENVIAR LIKES (MASSIVO)</button>
                <button onclick="run('/add_friend')" class="w-full py-4 border border-cyan-400 text-cyan-400 rounded-2xl font-bold hover:bg-cyan-400 hover:text-black transition">PEDIDO DE AMIZADE</button>
                <button onclick="run('/spam')" class="w-full py-4 border border-red-500 text-red-500 rounded-2xl font-bold hover:bg-red-500 hover:text-white transition">SPAM INVITE (TODAS CONTAS)</button>
                <button onclick="stopOp()" class="w-full py-3 bg-red-800 text-white rounded-xl font-bold border-2 border-red-500 shadow-lg">PARAR OPERAÇÕES (STOP)</button>
                <hr class="opacity-10">
                <input id="team" placeholder="CÓDIGO DE EQUIPE" class="input-4d">
                <input id="games" type="number" placeholder="QTD PARTIDAS" class="input-4d">
                <button onclick="runStart()" class="w-full py-4 bg-purple-600 rounded-2xl font-bold">INICIAR KERNEL BOT</button>
            </div>
            <div class="lg:col-span-2 glass p-10 h-[600px] flex flex-col">
                <h3 class="text-gray-500 font-bold mb-6">LIVE NET_LOGS</h3>
                <div id="logs" class="flex-1 overflow-y-auto space-y-4 pr-4"></div>
            </div>
        </div>
    </div>
    {% endif %}

    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('bg-canvas'), alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        const geometry = new THREE.TorusGeometry(10, 3, 16, 100);
        const material = new THREE.MeshBasicMaterial({ color: 0x00f2ff, wireframe: true });
        const torus = new THREE.Mesh(geometry, material);
        scene.add(torus);
        camera.position.z = 30;
        function animate() {
            requestAnimationFrame(animate);
            torus.rotation.x += 0.01; torus.rotation.y += 0.005;
            renderer.render(scene, camera);
        }
        animate();

        function checkPass(url) {
            let p = prompt("CHAVE DE CRIPTOGRAFIA:");
            if(p) window.location.href = url + "?key=" + btoa(p);
        }
        function run(route) {
            const u = document.getElementById('uid').value;
            fetch(`${route}?uid_alvo=${u}`).then(r=>r.json()).then(d=>alert('Status: '+d.status));
        }
        function runStart() {
            const t = document.getElementById('team').value;
            const g = document.getElementById('games').value;
            fetch(`/start?codeteam=${t}&maxgame=${g}`).then(r=>r.json()).then(d=>alert('Bot: '+d.status));
        }
        function stopOp() {
            fetch('/stop_spam').then(r=>r.json()).then(d=>alert(d.status));
        }
        setInterval(() => {
            const logBox = document.getElementById('logs');
            if(logBox) {
                fetch('/api/logs').then(r=>r.json()).then(data => {
                    logBox.innerHTML = data.map(l => `<div class="p-4 bg-white/5 rounded-2xl border-l-4 border-cyan-400 animate-pulse text-xs"><span class="opacity-30">[${l.time}]</span> ${l.msg}</div>`).join('');
                });
            }
        }, 3000);
    </script>
</body>
</html>
"""

# ===============================================
# 🛡️ SEGURANÇA E MIDDLEWARE (JSON AUTO)
# ===============================================

BAN_HTML = """
<!DOCTYPE html>
<html>
<body style="background:#000; color:red; font-family:monospace; text-align:center; padding-top:100px;">
    <h1 style="font-size:100px;">BANIDO</h1>
    <p>Seu IP {{ ip }} foi banido da rede Thayson.</p>
    <p>Motivo: {{ info.reason }}</p>
    <p>Expira em: {{ info.expires }}</p>
    <br><br>
    <a href="/download_ban_report" style="color:#fff; background:red; padding:20px; text-decoration:none; font-weight:bold; border-radius:10px;">BAIXAR RELATÓRIO_SEGURANÇA.ZIP</a>
</body>
</html>
"""

@app.route('/download_ban_report')
def ban_zip():
    ip = request.remote_addr
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, 'w') as zf:
        zf.writestr('AVISO_BAN.txt', f"IP: {ip}\nStatus: Blacklisted\nMotivo: Tentativa de invasao ou abuso de rede.")
        zf.writestr('SECURITY.html', "<h1>ACESSO NEGADO</h1><p>O sistema Thayson Master detectou anomalias no seu IP.</p>")
    mem.seek(0)
    return send_file(mem, mimetype='application/zip', as_attachment=True, download_name='Relatorio_Thayson.zip')

# ===============================================
# 🚀 ROTAS FLASK (COM PERSISTÊNCIA JSON)
# ===============================================

@app.route('/')
def home():
    if 'user' not in session: return render_template_string(HTML_INTERFACE, page='login')
    return render_template_string(HTML_INTERFACE, page='choice')

@app.route('/auth/login', methods=['POST'])
def auth_login():
    user = request.form.get('user').strip()
    ip = request.remote_addr
    
    # Valida Nomes Duplicados
    if user in USER_DB and USER_DB[user].get('ip') != ip:
        return "NOME DE USUÁRIO JÁ REGISTRADO POR OUTRO IP", 403

    # Salva no contas.json
    USER_DB[user] = {
        "ip": ip,
        "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Ativo"
    }
    save_json(ACCOUNTS_FILE, USER_DB)
    
    session['user'] = user
    ADMIN_CONFIG["active_users"][user] = ip
    log_event(f"Login detectado: {user} ({ip})")
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/panel')
def page_panel():
    try:
        pw = base64.b64decode(request.args.get('key')).decode()
        if pw != ADMIN_CONFIG_DB["app_password"]: return "SENHA INCORRETA", 403
        return render_template_string(HTML_INTERFACE, page='panel')
    except: return "ERRO DE ENTRADA", 400

@app.route('/admin')
def page_admin():
    try:
        pw = base64.b64decode(request.args.get('key')).decode()
        if pw != ADMIN_CONFIG_DB["admin_password"]: return "ACESSO NEGADO: Senha Master Incorreta", 403
        
        # Gera lista de usuários para o SELECT do BAN
        user_options = "".join([f'<option value="{u}">{u} ({d["ip"]})</option>' for u, d in USER_DB.items()])

        return render_template_string("""
            <div style="background:#000; color:#00f2ff; font-family:sans-serif; padding:50px; min-height:100vh;">
                <h1>THAYSON MASTER - GRADE ADMINISTRATIVA</h1>
                <hr style="opacity:0.2">
                <div style="margin-top:30px; display:grid; gap:20px;">
                    <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px;">
                        <h3>Alterar Senha do Painel Usuário (App)</h3>
                        <input id="new_app" placeholder="Nova senha app" style="padding:10px; border-radius:5px; border:none;">
                        <button onclick="change('app')" style="padding:10px; background:#00f2ff; border:none; border-radius:5px; cursor:pointer;">Atualizar</button>
                    </div>
                    
                    <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px;">
                        <h3 style="color:red;">⚙️ GESTÃO DE BANIMENTOS</h3>
                        <select id="ban_user" style="padding:10px; border-radius:5px; width:100%; margin-bottom:10px;">
                            <option value="">Selecione um Usuário...</option>
                            """ + user_options + """
                        </select>
                        <input id="ban_reason" placeholder="Motivo do Banimento" style="padding:10px; border-radius:5px; border:none; width:100%; margin-bottom:10px;">
                        <label>Data para Desbanir:</label>
                        <input type="datetime-local" id="ban_date" style="padding:10px; border-radius:5px; border:none; width:100%; margin-bottom:10px;">
                        <button onclick="applyBan()" style="padding:15px; background:red; color:white; border:none; border-radius:10px; cursor:pointer; width:100%; font-weight:bold;">APLICAR BANIMENTO E BLOQUEAR IP</button>
                    </div>
                </div>
                <br><a href="/" style="color:#fff; text-decoration:none;">← Voltar ao Início</a>
                <script>
                    function change(type) {
                        const val = (type==='app') ? document.getElementById('new_app').value : document.getElementById('new_admin').value;
                        fetch(`/admin/action?action=change_pass&type=${type}&value=${val}`)
                        .then(r => r.json()).then(d => alert('Configuração salva!'));
                    }
                    function applyBan() {
                        const user = document.getElementById('ban_user').value;
                        const reason = document.getElementById('ban_reason').value;
                        const date = document.getElementById('ban_date').value;
                        if(!user || !date) return alert('Selecione o usuário e a data!');
                        fetch(`/admin/action?action=ban&user=${user}&reason=${reason}&date=${date}`)
                        .then(r => r.json()).then(d => {
                            alert(d.status);
                            location.reload();
                        });
                    }
                </script>
            </div>
        """)
    except: return "ERRO", 400

@app.route('/admin/action')
def admin_action():
    act = request.args.get('action')
    if act == 'change_pass':
        t = request.args.get('type')
        val = request.args.get('value')
        if t == 'app': ADMIN_CONFIG_DB['app_password'] = val
        else: ADMIN_CONFIG_DB['admin_password'] = val
        save_json(CONFIG_FILE, ADMIN_CONFIG_DB)
    elif act == 'ban':
        u = request.args.get('user')
        reason = request.args.get('reason', 'Violação de Termos')
        date = request.args.get('date') # Formato: 2023-10-27T15:30
        
        # Pega IP do banco de dados persistente
        ip = USER_DB.get(u, {}).get('ip')
        if ip:
            BANNED_DB[ip] = {
                "expires": date, 
                "reason": reason,
                "user": u
            }
            save_json(BANS_FILE, BANNED_DB)
            return jsonify({"status": f"Usuário {u} banido até {date}!"})
        return jsonify({"status": "Erro: Usuário não encontrado no contas.json"})
    return jsonify({"status": "OK"})

@app.route('/api/logs')
def api_logs(): return jsonify(ADMIN_CONFIG["logs"])

# ===============================================
# ⚙️ FUNÇÕES DO KERNEL FF (100% ORIGINAL - SEM CORTES)
# ===============================================

ReleaseVersion, version, Version = "OB51", "1.118.1", "2019118695"
Hr = {
    'Connection': "Keep-Alive", 'Accept-Encoding': "gzip", 'Content-Type': "application/octet-stream", 
    'Expect': "100-continue", 'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 
    'ReleaseVersion': ReleaseVersion, 'Content-Type': "application/x-www-form-urlencoded"
}

async def encrypted_proto(encoded_data):
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_data, AES.block_size)
    return cipher.encrypt(padded_message)

async def Login_And_Other_User_Agent(): return "Dalvik/2.1.0 (Linux; U; Android 11; SM-A515F Build/RP1A.200720.011)"
async def Connect_Garana_User_Agent(): return "GarenaMSDK/4.1.0P3(SM-A515F;Android 11;pt-BR;BRA;)"

async def MajorLogin(Payload, login_url_from_session):
    try:
        url = f"{login_url_from_session}/MajorLogin"
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        Hr['User-Agent'] = (await Login_And_Other_User_Agent())
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=Payload, headers=Hr, ssl=ssl_context) as response:
                if response.status == 200: return await response.read()
                return None
    except Exception: return None

async def GetLoginData(URL, Payload, Token):
    try:
        url = f"{URL}/GetLoginData"
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        Hr['Authorization']= f"Bearer {Token}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=Payload, headers=Hr, ssl=ssl_context) as response:
                if response.status == 200: return await response.read()
                return None
    except Exception: return None

async def DecryptMajorLogin(MajorLoginResponse):
    try:
        proto = MajorLogin_pb2.MajorLoginRes()
        proto.ParseFromString(MajorLoginResponse)
        return proto
    except Exception: return None

async def DecryptGetLoginData(GetLoginDataResponse):
    try:
        proto = GetLoginData_pb2.GetLoginData()
        proto.ParseFromString(GetLoginDataResponse)
        return proto
    except Exception: return None

async def FinalTokenToGetOnline(Target, Token, Timestamp, key, iv):
    try:
        UidHex = hex(Target)[2:]
        UidLength = len(UidHex)
        EncryptedTimeStamp = await DecodeHex(Timestamp)
        EncryptedAccountToken = Token.encode().hex()
        EncryptedPacket = await EncryptPacket(EncryptedAccountToken, key, iv)
        EncryptedPacketLength = hex(len(EncryptedPacket) // 2)[2:]
        if UidLength == 9: headers = '0000000'
        elif UidLength == 8: headers = '00000000'
        elif UidLength == 10: headers = '000000'
        elif UidLength == 7: headers = '000000000'
        else: headers = '0000000'
        return f"0115{headers}{UidHex}{EncryptedTimeStamp}00000{EncryptedPacketLength}{EncryptedPacket}"
    except Exception: return None
    
async def EncryptLoginPayload(open_id, access_token):
    try:
        fields = {
            3: str(datetime.now())[:-7], 4: "free fire", 5: 1, 7: version,
            8: "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)",
            9: "Handheld", 10: "Verizon", 11: "WIFI", 12: 1920, 13: 1080,
            14: "280", 15: "ARM64 FP ASIMD AES VMH | 2865 | 4", 16: 3003,
            17: "Adreno (TM) 640", 18: "OpenGL ES 3.1 v1.46",
            19: "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57",
            20: "223.191.51.89", 21: "en", 22: open_id, 23: "4", 24: "Handheld",
            25: "07@Q", 29: access_token, 30: 1, 41: "Verizon", 42: "WIFI",
            57: "7428b253defc164018c604a1ebbfebdf", 60: 36235, 61: 31335,
            62: 2519, 63: 703, 64: 25010, 65: 26628, 66: 32992, 67: 36235,
            73: 3, 74: "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64",
            76: 1, 77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk",
            78: 3, 79: 2, 81: "64", 83: Version, 86: "OpenGLES2", 87: 16383,
            88: 4, 89: b"FwQVTgUPX1UaUllDDwcWCRBpWA0UOQsVAVsnWlBaO1kFYg==",
            92: 13564, 93: "android",
            94: "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY=",
            95: 110009, 97: 1, 98: 1, 99: "4", 100: "4"
        }
        return (await encrypted_proto(await CreateProtobufPacket(fields)))
    except Exception: return None

async def GeNeRaTeAccEss(Uid , Password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    data = {"uid": Uid, "password": Password, "response_type": "token", "client_type": "2", "client_id": "100067"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                d = await response.json()
                return d.get("open_id"), d.get("access_token")
            return None, None

def log_event(msg):
    ADMIN_CONFIG["logs"].insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "msg": msg})

def Encrypt_ID_Friend(x):
    try: x = int(x)
    except: return ""
    dec = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
    xxx = ['1', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
    x = x / 128
    if x > 128:
        x = x / 128
        if x > 128:
            x = x / 128
            if x > 128:
                x = x / 128
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                m = (n - int(strn)) * 128
                return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
            else:
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
    return ""

def encrypt_api_friend(plain_text):
    try: plain_text = bytes.fromhex(plain_text)
    except: return ""
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plain_text, AES.block_size)).hex()

async def send_friend_logic(bot_name, config, target_uid):
    open_id, access_token = await GeNeRaTeAccEss(config[0], config[1])
    if not open_id: return False
    payload_login = await EncryptLoginPayload(open_id, access_token)
    major_resp = await MajorLogin(payload_login, config[2])
    if not major_resp: return False
    decrypt_major = await DecryptMajorLogin(major_resp)
    token = decrypt_major.token
    url = "https://client.us.freefiremobile.com/RequestAddingFriend"
    id_encrypted = Encrypt_ID_Friend(target_uid)
    if not id_encrypted: return False
    data0 = "08c8b5cfea1810" + id_encrypted + "18012008"
    data_hex = encrypt_api_friend(data0)
    data = bytes.fromhex(data_hex)
    headers = { "Content-Type": "application/octet-stream", "X-GA": "v1 1", "ReleaseVersion": "OB51", "Authorization": f"Bearer {token}", "User-Agent": "Free Fire/2019117061 CFNetwork/1399 Darwin/22.1.0" }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data, ssl=False) as resp:
                return resp.status == 200
    except: return False

async def send_like_logic(bot_name, config, target_uid):
    open_id, access_token = await GeNeRaTeAccEss(config[0], config[1])
    if not open_id: return False
    payload_login = await EncryptLoginPayload(open_id, access_token)
    major_resp = await MajorLogin(payload_login, config[2])
    if not major_resp: return False
    decrypt_major = await DecryptMajorLogin(major_resp)
    token = decrypt_major.token
    visit_url = "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
    try:
        data_packet = bytes.fromhex(encrypt_api("08" + Encrypt_ID(str(target_uid)) + "1801"))
        headers = {"ReleaseVersion": ReleaseVersion, "X-GA": "v1 1", "Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"}
        async with aiohttp.ClientSession() as session:
            async with session.post(visit_url, headers=headers, data=data_packet, ssl=False) as resp:
                return resp.status == 200
    except: return False

class FF_CLIENT:
    def __init__(self, session: Session, ff_account_config):
        self.session = session 
        self.ff_account_config = ff_account_config 
        self.key = None; self.iv = None; self.BotUid = None; self.BotToken = None
        self.URL = None; self.InvitePlayerId = self.session.ff_target_uid
        self.StatusData = None; self.SquadData = None; self.MatchmakingData = None
        self.online_writer = None 

    async def SendPacket(self, Packet):  
        if self.online_writer and not self.online_writer.is_closing():
            try:
                self.online_writer.write(Packet)
                await self.online_writer.drain()
            except: pass
    
    async def InviteAcceptedRejectedStatus(self):  
        s = self.session
        s.invite_sent_time = datetime.now() 
        while True:
            await asyncio.sleep(1) 
            if s.invite_sent_time and (datetime.now() - s.invite_sent_time).total_seconds() > s.invite_timeout_seconds:
                s.invite_sent_time = None 
                s.ff_status_message = "Sessão encerrada por timeout do convite."
                return {'timeout': True} 
            if self.SquadData != None:  
                try: InviteData = json.loads(self.SquadData)  
                except: self.SquadData = None; continue
                if '4' in InviteData and InviteData['4']['data'] == 2:  
                    self.SquadData = None; continue 
                elif '4' in InviteData and InviteData['4']['data'] in [6, 50] and '5' in InviteData:
                    s.invite_sent_time = None 
                    return InviteData  
      
    async def MatchmakingStatus(self):  
        while True:
             await asyncio.sleep(0.1)
             if self.MatchmakingData != None:  
                try: MatchStartData = json.loads(self.MatchmakingData)  
                except: self.MatchmakingData = None; continue
                self.MatchmakingData = None  
                if "4" in MatchStartData and MatchStartData["4"]["data"] == 5: return MatchStartData  
      
    async def SlwdLoop(self, FinalTokn):  
        s = self.session 
        try:
            while s.current_session_games < s.max_games and not s.ff_status_message.startswith("Sessão encerrada por timeout"): 
                s.ff_status_message = f"Verificando Status. Restam: {s.max_games - s.current_session_games}"
                StatusPlayerId = await PlayerStatus(self.InvitePlayerId, self.key, self.iv)  
                await self.SendPacket(StatusPlayerId)
                await asyncio.sleep(1) 
                
                if self.StatusData != None:
                    try: StatusData = json.loads(self.StatusData); self.StatusData = None
                    except: self.StatusData = None; await asyncio.sleep(1); continue 
                    status_path = StatusData.get("5", {}).get("data", {}).get("1", {}).get("data", {})
                    if isinstance(status_path, dict) and "3" in status_path and "11" in status_path:
                        team_status = status_path["3"].get("data")
                        is_in_squad = status_path["11"].get("data")
                        if team_status == 1 and is_in_squad == 1:
                            await self.SendPacket(await SwitchLoneWolf(self.key, self.iv)); await asyncio.sleep(1)
                            await self.SendPacket(await SwitchLoneWolfDule(self.BotUid, self.key, self.iv)); await asyncio.sleep(1)
                            await self.SendPacket(await InvitePlayer(self.InvitePlayerId, self.key, self.iv))
                            InviteStatus = await self.InviteAcceptedRejectedStatus()
                            if not InviteStatus or 'timeout' in InviteStatus: return 
                        elif team_status == 2 and is_in_squad == 1:
                            player_count = status_path.get("9", {}).get("data", 0)
                            max_players = status_path.get("10", {}).get("data", 0) + 1
                            if player_count == max_players:
                                await self.SendPacket(await SwitchLoneWolf(self.key, self.iv)); await asyncio.sleep(1)
                                await self.SendPacket(await StartGame(self.BotUid, self.key, self.iv))
                                MatchStartData = await self.MatchmakingStatus()  
                                if not MatchStartData: return 
                                if "4" in MatchStartData and MatchStartData["4"]["data"] == 5:
                                    await asyncio.sleep(30)
                                    s.current_session_games += 1; s.ff_total_games += 1 
                                    await self.SendPacket(await LeaveTeam(self.BotUid, self.key, self.iv))
                                    self.StatusData = None; self.SquadData = None
                                    if s.current_session_games >= s.max_games: return 
                                    await asyncio.sleep(5); continue 
                            elif player_count < max_players:
                                await self.SendPacket(await InvitePlayer(self.InvitePlayerId, self.key, self.iv)); await asyncio.sleep(1)
                else:  self.StatusData = None  
        except asyncio.CancelledError: raise

    async def TcpOnline(self, FinalTokn):  
        s = self.session
        try:
            while s.current_session_games < s.max_games and not s.ff_status_message.startswith("Sessão encerrada por timeout"):
                try:  
                    reader, writer = await asyncio.open_connection(self.OnlineIP, int(self.OnlinePort))  
                    self.online_writer = writer  
                    BytesPayload = bytes.fromhex(FinalTokn)  
                    self.online_writer.write(BytesPayload)  
                    await self.online_writer.drain()  
                    self.slwd_task = asyncio.create_task(self.SlwdLoop(FinalTokn))
                    while not self.slwd_task.done():  
                        try:
                            self.data2 = await asyncio.wait_for(reader.read(9999), timeout=1.0)
                            if not self.data2: break
                            data2_hex = self.data2.hex()
                            if data2_hex.startswith("0300"): self.MatchmakingData = await DecodeProtobufPacket(data2_hex[10:])
                            elif data2_hex.startswith("0500"): self.SquadData = await DecodeProtobufPacket(data2_hex[10:])
                            elif data2_hex.startswith("0f00"): self.StatusData = await DecodeProtobufPacket(data2_hex[10:])
                        except asyncio.TimeoutError: continue
                    if self.slwd_task.done(): break 
                except: await asyncio.sleep(5)
                finally:
                    if self.online_writer:
                        try:
                            self.online_writer.close()
                            await self.online_writer.wait_closed()
                        except: pass
                        self.online_writer = None
        except asyncio.CancelledError: raise

    async def Main(self):  
        s = self.session 
        Uid, Password, LoginUrl = self.ff_account_config
        try:
            open_id, access_token = await GeNeRaTeAccEss(Uid, Password)  
            if not open_id or not access_token: return 
            Payload = await EncryptLoginPayload(open_id, access_token)  
            MajorLoginResponse = await MajorLogin(Payload, LoginUrl)  
            if not MajorLoginResponse: return 
            MajorLoginDecrypt = await DecryptMajorLogin(MajorLoginResponse)  
            self.BotUid = MajorLoginDecrypt.account_uid; self.BotToken = MajorLoginDecrypt.token; self.URL = MajorLoginDecrypt.url  
            self.key = MajorLoginDecrypt.key; self.iv = MajorLoginDecrypt.iv; TimeStamp = MajorLoginDecrypt.timestamp  
            GetLoginDataResponse = await GetLoginData(self.URL, Payload, self.BotToken)  
            if not GetLoginDataResponse: return 
            GetLoginDataDecrypt = await DecryptGetLoginData(GetLoginDataResponse)  
            self.OnlineIP , self.OnlinePort = GetLoginDataDecrypt.Online_IP_Port.split(":")  
            s.is_running = True
            FinalToken = await FinalTokenToGetOnline(int(self.BotUid), self.BotToken, int(TimeStamp), self.key, self.iv)  
            await self.TcpOnline(FinalToken)
        except asyncio.CancelledError: pass
        finally:
            if self.BotUid and self.key:
                try:
                    tr, tw = await asyncio.open_connection(self.OnlineIP, int(self.OnlinePort))
                    tw.write(bytes.fromhex(await FinalTokenToGetOnline(int(self.BotUid), self.BotToken, int(time.time()), self.key, self.iv)))
                    await tw.drain()
                    tw.write(await LeaveTeam(self.BotUid, self.key, self.iv))
                    await tw.drain()
                    tw.close()
                except: pass
            s.is_running = False
            s.ff_target_uid = None; s.ff_loop = None; s.ff_kernel_task = None

# ===============================================
# ⚙️ LÓGICA DE SPAM MULTI-CONTAS (CORREÇÃO)
# ===============================================

async def single_bot_spam(bot_name, config, target_uid):
    uid, psw, login_url = config
    open_id, access_token = await GeNeRaTeAccEss(uid, psw)
    if not open_id: return
    payload = await EncryptLoginPayload(open_id, access_token)
    major_resp = await MajorLogin(payload, login_url)
    if not major_resp: return
    major_dec = await DecryptMajorLogin(major_resp)
    bot_uid, token, key, iv = major_dec.account_uid, major_dec.token, major_dec.key, major_dec.iv
    log_data_resp = await GetLoginData(major_dec.url, payload, token)
    if not log_data_resp: return
    log_dec = await DecryptGetLoginData(log_data_resp)
    ip, port = log_dec.Online_IP_Port.split(":")
    
    try:
        reader, writer = await asyncio.open_connection(ip, int(port))
        final_tok = await FinalTokenToGetOnline(int(bot_uid), token, int(major_dec.timestamp), key, iv)
        writer.write(bytes.fromhex(final_tok))
        await writer.drain()
        
        while not STOP_SPAM_EVENT.is_set():
            # 1. Criar Squad / Mudar Modo
            writer.write(await SwitchLoneWolf(key, iv))
            await writer.drain()
            # 2. Convidar
            writer.write(await InvitePlayer(target_uid, key, iv))
            await writer.drain()
            await asyncio.sleep(0.05) # Delay ultra rápido
            # 3. Sair para Resetar Convite
            writer.write(await LeaveTeam(bot_uid, key, iv))
            await writer.drain()
            await asyncio.sleep(0.05)
            
        writer.close()
        await writer.wait_closed()
    except: pass

def worker_spam_hub(target_uid):
    STOP_SPAM_EVENT.clear()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Lança TODAS as contas ao mesmo tempo
    tasks = [single_bot_spam(name, config, target_uid) for name, config in FF_ACCOUNTS_BR.items()]
    loop.run_until_complete(asyncio.gather(*tasks))

def run_ff_kernel(session: Session, ff_account_config):
    session._stop_event.clear()
    session.ff_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(session.ff_loop)
    client = FF_CLIENT(session, ff_account_config)
    try:
        session.ff_kernel_task = session.ff_loop.create_task(client.Main())
        session.ff_loop.run_until_complete(session.ff_kernel_task)
    except: pass

@app.route('/add_friend', methods=['GET'])
def add_friend():
    uid_alvo = request.args.get('uid_alvo')
    log_event(f"Solicitando amizade para: {uid_alvo}")
    async def run_p():
        tasks = [send_friend_logic(name, config, uid_alvo) for name, config in list(FF_ACCOUNTS_BR.items())[:50]]
        return await asyncio.gather(*tasks, return_exceptions=True)
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    results = loop.run_until_complete(run_p())
    return jsonify({"status": "Sucesso", "enviados": sum(1 for r in results if r is True)})

@app.route('/like_all', methods=['GET'])
def like_all():
    uid_alvo = request.args.get('uid_alvo')
    log_event(f"Likes massivos para: {uid_alvo}")
    async def run_p():
        tasks = [send_like_logic(name, config, uid_alvo) for name, config in FF_ACCOUNTS_BR.items()]
        return await asyncio.gather(*tasks, return_exceptions=True)
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    results = loop.run_until_complete(run_p())
    return jsonify({"status": "Sucesso", "total": len(results)})

@app.route('/spam', methods=['GET'])
def spam_route():
    uid_alvo = request.args.get('uid_alvo')
    log_event(f"ATAQUE SPAM INICIADO (Todas Contas): {uid_alvo}")
    threading.Thread(target=worker_spam_hub, args=(uid_alvo,), daemon=True).start()
    return jsonify({"status": "Ataque Massivo em execução!"})

@app.route('/stop_spam', methods=['GET'])
def stop_spam():
    STOP_SPAM_EVENT.set()
    log_event("SINAL DE PARADA ENVIADO PELO USUÁRIO.")
    return jsonify({"status": "Operações interrompidas"})

@app.route('/start', methods=['GET'])
def start_games():
    codeteam = request.args.get('codeteam')
    maxgame = int(request.args.get('maxgame', 1))
    log_event(f"Iniciando Bot Partida: {codeteam}")
    bot_name = "BOT_01"
    session_bot = SESSION_MANAGER.get_session(bot_name)
    if session_bot.is_running: return jsonify({"status": "Erro - Já em execução"}), 400
    session_bot.ff_target_uid = codeteam
    session_bot.max_games = maxgame
    threading.Thread(target=run_ff_kernel, args=(session_bot, FF_ACCOUNTS_BR[bot_name]), daemon=True).start()
    return jsonify({"status": "Bot Iniciado"})

if __name__ == '__main__':
    print("🔥 SISTEMA THAYSON MASTER INICIANDO...")
    app.run(host='0.0.0.0', port=5000, threaded=True)
