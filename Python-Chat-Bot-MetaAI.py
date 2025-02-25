import requests
import json
import time
import urllib
import uuid

""" Hàm này dùng để trích xuất giá trị giữa 2 chuỗi xác định (start_str và end_str) trong văn bản """
def trich_xuat_gia_tri(text: str, start_str: str, end_str: str) -> str:
    try:
        """ Tìm vị trí bắt đầu và kết thúc """
        start = text.index(start_str) + len(start_str)
        end = text.index(end_str, start)
        return text[start:end]
    except ValueError:
        return ""

""" Hàm này dùng để trích xuất thông tin chat từ phản hồi JSON """
def trich_xuat_chat(response_text):
    try:
        """ Khởi tạo đối tượng chứa thông tin tin nhắn của người dùng và trợ lý """
        latest_messages = {
            "user": "",
            "assistant": ""
        }

        """ Phân tích từng dòng JSON trong phản hồi """
        for line in response_text.split('\n'):
            if not line:
                continue

            try:
                json_data = json.loads(line)

                if "data" not in json_data:
                    continue

                node = json_data.get("data", {}).get("node", {})
                if not node:
                    continue

                """ Trích xuất thông tin tin nhắn của người dùng """
                user_msg = node.get("user_request_message", {})
                if user_msg and "snippet" in user_msg:
                    latest_messages["user"] = user_msg["snippet"]

                """ Trích xuất thông tin tin nhắn của trợ lý """
                bot_msg = node.get("bot_response_message", {})
                if bot_msg and "snippet" in bot_msg:
                    if bot_msg.get("streaming_state") == "OVERALL_DONE":
                        latest_messages["assistant"] = bot_msg["snippet"].replace("**", "")

            except json.JSONDecodeError:
                continue

        return latest_messages

    except Exception as e:
        print(f"Lỗi khi phân tích chat: {str(e)}")
        return {"user": "", "assistant": ""}


""" Thiết lập tiêu đề cho yêu cầu HTTP """
headers = {
  'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
  'sec-ch-ua-platform': "\"Windows\"",
  'sec-ch-ua': "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
  'sec-ch-ua-mobile': "?0",
  'origin': "https://www.meta.ai",
  'sec-fetch-site': "same-site",
  'sec-fetch-mode': "cors",
  'sec-fetch-dest': "empty",
  'referer': "https://www.meta.ai/",
  'accept-language': "vi-VN,vi;q=0.9",
  'priority': "u=1, i",
}


""" Tạo một phiên làm việc mới """
session = requests.Session()

""" Gửi yêu cầu GET để lấy thông tin cần thiết cho cookies """
response = session.get('https://meta.ai', headers=headers)
__csr = trich_xuat_gia_tri(response.text, '"client_revision":', ',"')
cookies = {
          "_js_datr": trich_xuat_gia_tri(response.text, '_js_datr":{"value":"', '",'),
          "datr": trich_xuat_gia_tri(response.text, 'datr":{"value":"', '",'),
          "lsd": trich_xuat_gia_tri(response.text, '"LSD",[],{"token":"', '"}'),
          "fb_dtsg": trich_xuat_gia_tri(response.text, 'DTSGInitData",[],{"token":"', '"'),
          "abra_csrf": trich_xuat_gia_tri(response.text, 'abra_csrf":{"value":"', '",')
      }


""" URL API cho yêu cầu POST """
url = "https://www.meta.ai/api/graphql/"

""" Payload với thông tin đăng nhập và các tham số yêu cầu """
payload = {
    "lsd": cookies["lsd"],
    "fb_api_caller_class": "RelayModern",
    "fb_api_req_friendly_name": "useAbraAcceptTOSForTempUserMutation",
    "variables": {
        "dob": "1999-01-01",
        "icebreaker_type": "TEXT",
        "__relay_internal__pv__WebPixelRatiorelayprovider": 1,
    },
    "doc_id": "7604648749596940",
}

payload = urllib.parse.urlencode(payload)

""" Thiết lập lại tiêu đề cho yêu cầu POST """
headers = {
      "content-type": "application/x-www-form-urlencoded",
      "cookie": f'_js_datr={cookies["_js_datr"]}; abra_csrf={cookies["abra_csrf"]}; datr={cookies["datr"]};',
      "sec-fetch-site": "same-origin",
      "x-fb-friendly-name": "useAbraAcceptTOSForTempUserMutation",
  }
response = session.post(url, headers=headers, data=payload)

""" Trích xuất access_token từ phản hồi """
auth_json = response.json()
access_token = auth_json["data"]["xab_abra_accept_terms_of_service"]["new_temp_user_auth"]["access_token"]

""" URL để gửi yêu cầu chat """
url = "https://graph.meta.ai/graphql?locale=user"

""" Vòng lặp chính để gửi và nhận tin nhắn """
while True:
  try:
      """ Nhận đầu vào từ người dùng """
      user_input = input("\nBạn: ")
      
      """ Nếu người dùng nhập 'exit' thì thoát khỏi vòng lặp """
      if user_input.lower() == 'exit':
          print("Tạm biệt!")
          break
          
      url = "https://graph.meta.ai/graphql?locale=user"
      
      """ Payload chứa thông tin cần thiết để gửi tin nhắn """
      payload = {
          'av': '0',
          'access_token': access_token,
          '__user': '0',
          '__a': '1',
          '__req': '5',
          '__hs': '20139.HYP:abra_pkg.2.1...0',
          'dpr': '1',
          '__ccg': 'GOOD',
          '__rev': '1020250634',
          '__s': 'ukq0lm:22y2yf:rx88gm',
          '__hsi': '7473469487460105169',
          '__dyn': '7xeUmwlEnwn8K2Wmh0no6u5U4e0yoW3q32360CEbo19oe8hw2nVE4W099w8G1Dz81s8hwnU2lwv89k2C1Fwc60D85m1mzXwae4UaEW4U2FwNwmE2eU5O0EoS0raazo11E2ZwrUdUco9E3Lwr86C1nw4xxW2W5-fwmU3yw',
          '__csr': trich_xuat_gia_tri(response.text, '"client_revision":', ',"'),
          '__comet_req': '46',
          'lsd': cookies['lsd'], 
          'jazoest': '', 
          '__spin_r': '1020250634',
          '__spin_b': 'trunk',
          '__spin_t': str(int(time.time() * 1000)),
          '__jssesw': '1',
          'fb_api_caller_class': 'RelayModern',
          'fb_api_req_friendly_name': 'useAbraSendMessageMutation',
          'variables': json.dumps({
              "message": {"sensitive_string_value": user_input},
              "externalConversationId": str(uuid.uuid4()), 
              "offlineThreadingId": str(int(time.time() * 1000)),
              "suggestedPromptIndex": None,
              "flashVideoRecapInput": {"images": []},
              "flashPreviewInput": None,
              "promptPrefix": None,
              "entrypoint": "ABRA__CHAT__TEXT",
              "icebreaker_type": "TEXT_V2",
              "attachments": [],
              "attachmentsV2": [],
              "activeMediaSets": None,
              "activeCardVersions": [],
              "activeArtifactVersion": None,
              "userUploadEditModeInput": None,
              "reelComposeInput": None,
              "qplJoinId": "fc43f4e563f41b383",
              "gkAbraArtifactsEnabled": False,
              "model_preference_override": None,
              "threadSessionId": str(uuid.uuid4()),
              "__relay_internal__pv__AbraPinningConversationsrelayprovider": False,
              "__relay_internal__pv__AbraArtifactsEnabledrelayprovider": False,
              "__relay_internal__pv__WebPixelRatiorelayprovider": 1,
              "__relay_internal__pv__AbraSearchInlineReferencesEnabledrelayprovider": True,
              "__relay_internal__pv__AbraComposedTextWidgetsrelayprovider": False,
              "__relay_internal__pv__AbraSearchReferencesHovercardEnabledrelayprovider": True,
              "__relay_internal__pv__AbraCardNavigationCountrelayprovider": True,
              "__relay_internal__pv__AbraDebugDevOnlyrelayprovider": False,
              "__relay_internal__pv__AbraHasNuxTourrelayprovider": True,
              "__relay_internal__pv__AbraQPSidebarNuxTriggerNamerelayprovider": "meta_dot_ai_abra_web_message_actions_sidebar_nux_tour",
              "__relay_internal__pv__AbraSurfaceNuxIDrelayprovider": "12177",
              "__relay_internal__pv__AbraFileUploadsrelayprovider": False,
              "__relay_internal__pv__AbraQPDocUploadNuxTriggerNamerelayprovider": "meta_dot_ai_abra_web_doc_upload_nux_tour",
              "__relay_internal__pv__AbraQPFileUploadTransparencyDisclaimerTriggerNamerelayprovider": "meta_dot_ai_abra_web_file_upload_transparency_disclaimer",
              "__relay_internal__pv__AbraUpsellsKillswitchrelayprovider": True,
              "__relay_internal__pv__AbraIcebreakerImagineFetchCountrelayprovider": 20,
              "__relay_internal__pv__AbraImagineYourselfIcebreakersrelayprovider": False,
              "__relay_internal__pv__AbraEmuReelsIcebreakersrelayprovider": False,
              "__relay_internal__pv__AbraArtifactsDisplayHeaderV2relayprovider": False,
              "__relay_internal__pv__AbraArtifactEditorDebugModerelayprovider": False,
              "__relay_internal__pv__AbraArtifactSharingrelayprovider": False,
              "__relay_internal__pv__AbraArtifactEditorSaveEnabledrelayprovider": False,
              "__relay_internal__pv__AbraArtifactEditorDownloadHTMLEnabledrelayprovider": False,
              "__relay_internal__pv__AbraArtifactsRenamingEnabledrelayprovider": False
          }),
          'server_timestamps': 'true',
          'doc_id': '9614969011880432'
      }

      """ Gửi tin nhắn và nhận phản hồi """
      response = session.post(url, data=payload, headers=headers)
      ai_response = trich_xuat_chat(response.text)
      """ In ra câu trả lời của AI """
      if ai_response:
          print("\nMeta AI:", ai_response)
      else:
          print("\nKhông thể lấy được câu trả lời. Vui lòng thử lại.")
      
      time.sleep(1)
      
  except Exception as e:
      print(f"\nCó lỗi xảy ra: {str(e)}")
      print("Đang thử lại...")
      time.sleep(2)
      continue
