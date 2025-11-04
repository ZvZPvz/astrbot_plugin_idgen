# -- coding: utf-8 --
import re
import random
import datetime
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Star, register
from email.policy import default

@register("IDUtil", "ZvZPvz", "生成/验证身份证号码插件", "1.0.0")
class IDUtil(Star): 
    
    # --- 內部數據池 ---
    # 香港出生年份 -> 字母映射 (根據資料)
    _HKID_YEAR_MAP = {
        (1980, 1988): "Z",
        (1989, 2005): "Y", # 截至 2005 年 3 月
        (2005, 2019): "S", # 自 2005 年 4 月起
        (2019, 2048): "N", # 自 2019 年 6 月起
    }
    # 香港首次登記字母 (非出生)
    _HKID_REG_LETTERS = ["K", "P", "R", "M", "F"]
    # 中國大陸地址碼池 (用於隨機生成)
    _CNID_AREA_POOL = ["110101", "310101", "440101", "440301", "510101"]

    # --- 幫助文檔 (v1.0.0) ---
    HELP_TEXT = """# 身份證號碼工具 (IDUtil) v1.0.0

## 命令格式
`/id_util <command> [value] [options]`

## 命令說明
- `help`: 顯示此幫助信息

---
### 號碼生成 (Gen)
(功能：隨機生成符合格式的完整號碼)
- `gen_cn <YYYYMMDD> [M|F]`: 
  隨機生成中國大陸ID。需提供8位生日。
  可選 [M](男) 或 [F](女) 指定性別。
- `gen_hk <YYYY>` 或 `gen_hk <Letter>`:
  隨機生成香港ID。
  可輸入年份 (如 1985) 自動匹配字母，或直接指定字母 (如 K)。

---
### 校驗碼計算 (Sum)
(功能：根據號碼本體計算校驗碼)
- `sum_cn <17位本體>`: 計算CNID的第18位校驗碼。
- `sum_hk <本體>`: 計算HKID的校驗碼 (如 G123456)。

---
### 號碼驗證 (Validate)
(功能：檢查完整號碼的校驗碼是否正確)
- `validate_cn <18位ID>`: 驗證CNID。
- `validate_hk <ID(C)>`: 驗證HKID (如 C123456(9))。

## 示例
- `/id_util gen_cn 19900101 M`: 生成中國大陸ID，出生日期為1990年1月1日，性別為男。
- `/id_util gen_cn 19900101 F`: 生成中國大陸ID，出生日期為1990年1月1日，性別為女。
- `/id_util gen_cn 19900101`: 生成中國大陸ID，出生日期為1990年1月1日，性別隨機。
- `/id_util gen_hk 1985`: 生成香港ID，出生年份為1985。
- `/id_util gen_hk K`: 生成香港ID，指定字母為K。
- `/id_util sum_cn 11010219840406970`: 計算中國大陸ID的校驗碼。
- `/id_util validate_cn 11010219840406970X`: 驗證中國大陸ID。
"""

    def _get_hkid_letter_val(self, char: str) -> int:
        if 'A' <= char <= 'Z':
            return ord(char) - ord('A') + 10
        if char == ' ':
            return 36
        return 0

    def _calculate_hkid_checksum(self, body: str):
        match = re.fullmatch(r'^([A-Z]{1,2})(\d{6})$', body.upper())
        if not match:
            return None, "格式錯誤 (應為 1-2 字母 + 6 數字)"
        
        letters, digits = match.groups()
        
        vals = []
        if len(letters) == 1:
            vals = [self._get_hkid_letter_val(' '), self._get_hkid_letter_val(letters[0])]
        else:
            vals = [self._get_hkid_letter_val(letters[0]), self._get_hkid_letter_val(letters[1])]
        
        vals.extend([int(d) for d in digits])
        weights = [9, 8, 7, 6, 5, 4, 3, 2]
        
        total_sum = sum(vals[i] * weights[i] for i in range(8))
        remainder = total_sum % 11
        
        if remainder == 0:
            checksum = '0'
        else:
            diff = 11 - remainder
            checksum = 'A' if diff == 10 else str(diff)
            
        return f"{body.upper()}({checksum})", "計算成功"

    def _validate_hkid(self, hkid: str):
        match = re.fullmatch(r'^([A-Z]{1,2})(\d{6})\(([0-9A])\)$', hkid.upper())
        if not match:
            return False, "格式錯誤 (應為 1-2 字母 + 6 數字 + (校驗碼))"
        
        letters, digits, checksum_char = match.groups()
        body = letters + digits
        
        # 使用 "計算" 功能來驗證
        expected_result, _ = self._calculate_hkid_checksum(body)
        
        if hkid.upper() == expected_result:
            return True, "有效"
        else:
            return False, f"無效 (校驗碼應為 {expected_result[-2:]})"

    def _calculate_cnid_checksum(self, body: str) -> str:
        if not re.fullmatch(r'^\d{17}$', body):
            return None
        
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        total_sum = sum(int(body[i]) * weights[i] for i in range(17))
        remainder = total_sum % 11
        check_val = (12 - remainder) % 11
        
        return body + ('X' if check_val == 10 else str(check_val))

    def _validate_cnid(self, cnid: str):
        match = re.fullmatch(r'^(\d{17})([\dX])$', cnid.upper())
        if not match:
            return False, "格式錯誤 (應為 18 位, 末位可為 X)"
        
        body, _ = match.groups()
        expected_full_id = self._calculate_cnid_checksum(body)
        
        if cnid.upper() == expected_full_id:
            return True, "有效"
        else:
            return False, f"無效 (校驗碼應為 {expected_full_id[-1]})"

    # --- (新) 號碼生成 (Gen) 邏輯 ---

    def _gen_cnid(self, yyyymmdd: str, sex: str = None):
        """生成中國大陸ID"""
        try:
            datetime.datetime.strptime(yyyymmdd, '%Y%m%d')
        except ValueError:
            return None, "日期格式錯誤 (應為 YYYYMMDD)"
        
        area = random.choice(self._CNID_AREA_POOL)
        
        # 順序碼 (3位)
        seq_num = random.randint(0, 999)
        
        if sex:
            if sex.upper() == 'M': # 男 (單數)
                if seq_num % 2 == 0:
                    seq_num = (seq_num + 1) % 1000 # 變為奇數
            elif sex.upper() == 'F': # 女 (雙數)
                if seq_num % 2 != 0:
                    seq_num = (seq_num + 1) % 1000 # 變為偶數 (999->000)

        seq_str = f"{seq_num:03d}"
        
        body = area + yyyymmdd + seq_str
        full_id = self._calculate_cnid_checksum(body)
        return full_id, f"生成成功 (地區: {area}, 順序碼: {seq_str}, 性別: {sex or '隨機'})"

    def _gen_hkid(self, prefix_input: str):
        """生成香港ID"""
        letter = ""
        # 檢查輸入是年份還是字母
        if re.fullmatch(r'^\d{4}$', prefix_input):
            year = int(prefix_input)
            found = False
            for (start, end), char in self._HKID_YEAR_MAP.items():
                if start <= year <= end:
                    letter = char
                    found = True
                    break
            if not found:
                if year < 1980:
                    return None, f"年份 {year} 太早，請使用首次登記字母 (如 K, P, R, M, F) 或 1980 年後的年份。"
                else: # 備用
                     letter = "N"
        
        elif re.fullmatch(r'^[A-Z]{1,2}$', prefix_input.upper()):
            letter = prefix_input.upper()
        
        else:
            return None, "輸入格式錯誤 (應為 4 位年份 YYYY 或 1-2 位字母)"

        # 隨機 6 位數字
        digits = f"{random.randint(0, 999999):06d}"
        body = letter + digits
        
        result, _ = self._calculate_hkid_checksum(body)
        return result, f"生成成功 (使用字母: {letter})"

    # --- 主命令處理程序 ---
    
    @filter.command("id_util")
    async def id_util(self, event: AstrMessageEvent, arg1: str = "", arg2: str = "", arg3: str = ""):
        """
        主命令入口，解析參數並分發到對應的處理函數。
        """
        if not arg1 or arg1.lower() == "help":
            yield event.plain_result(self.HELP_TEXT)
            return

        command = arg1.lower()
        
        if command not in ["gen_cn", "gen_hk", "sum_cn", "sum_hk", "validate_cn", "validate_hk"]:
            yield event.plain_result(f"請提供必要的參數。\n使用 `/id_util help` 查看幫助。")
            return

        value = arg2

        try:
            # --- Gen ---
            if command == "gen_cn":
                sex = arg3 if arg3 else None
                result, msg = self._gen_cnid(value, sex)
                if result:
                    yield event.plain_result(f"生成中國大陸ID: {result}\n信息: {msg}")
                else:
                    yield event.plain_result(f"錯誤: {msg}")

            elif command == "gen_hk":
                result, msg = self._gen_hkid(value)
                if result:
                    yield event.plain_result(f"生成香港ID: {result}\n信息: {msg}")
                else:
                    yield event.plain_result(f"錯誤: {msg}")

            # --- Sum ---
            elif command == "sum_cn":
                if not re.fullmatch(r'^\d{17}$', value):
                     yield event.plain_result(f"錯誤: 格式錯誤 (應為 17 位數字)")
                     return
                result = self._calculate_cnid_checksum(value)
                yield event.plain_result(f"中國大陸ID (17位本體): {value}\n計算結果 (完整號碼): {result}")

            elif command == "sum_hk":
                result, msg = self._calculate_hkid_checksum(value)
                if result:
                    yield event.plain_result(f"香港ID (本體): {value}\n計算結果: {result}")
                else:
                    yield event.plain_result(f"錯誤: {msg}")

            # --- Validate ---
            elif command == "validate_cn":
                is_valid, msg = self._validate_cnid(value)
                result_text = "有效" if is_valid else "無效"
                yield event.plain_result(f"中國大陸ID: {value}\n驗證結果: {result_text}\n信息: {msg}")
            
            elif command == "validate_hk":
                is_valid, msg = self._validate_hkid(value)
                result_text = "有效" if is_valid else "無效"
                yield event.plain_result(f"香港ID: {value}\n驗證結果: {result_text}\n信息: {msg}")
                
            else:
                yield event.plain_result(f"未知的命令: {command}\n使用 `/id_util help` 查看幫助。")

        except Exception as e:
            yield event.plain_result(f"處理時發生內部錯誤: {e}")
