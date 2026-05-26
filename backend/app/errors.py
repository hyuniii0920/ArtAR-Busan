"""프론트 분기를 위한 code 포함 에러 응답.

표준 형태: {"success": false, "error": {"code": "...", "message": "..."}}
기존 라우터의 HTTPException은 그대로 두고, 신규 회원가입/승인 라우터에서 사용한다.
"""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {"code": exc.code, "message": exc.message},
        },
    )


# --- 자주 쓰는 에러 ---
def invalid_credentials() -> AppError:
    return AppError(401, "INVALID_CREDENTIALS", "이메일 또는 비밀번호가 올바르지 않습니다.")


def email_already_exists() -> AppError:
    return AppError(409, "EMAIL_ALREADY_EXISTS", "이미 사용 중인 이메일입니다.")


def email_required() -> AppError:
    return AppError(422, "EMAIL_REQUIRED", "이메일을 입력해 주세요.")


def password_required() -> AppError:
    return AppError(422, "PASSWORD_REQUIRED", "비밀번호를 입력해 주세요.")


def museum_name_required() -> AppError:
    return AppError(422, "MUSEUM_NAME_REQUIRED", "기관명을 입력해 주세요.")


def contact_required() -> AppError:
    return AppError(422, "CONTACT_REQUIRED", "연락처를 입력해 주세요.")


def user_not_found() -> AppError:
    return AppError(404, "USER_NOT_FOUND", "사용자를 찾을 수 없습니다.")


def not_museum() -> AppError:
    return AppError(400, "NOT_MUSEUM", "미술관 계정이 아닙니다.")


def not_logged_in() -> AppError:
    return AppError(401, "NOT_LOGGED_IN", "로그인이 필요합니다.")


def forbidden() -> AppError:
    return AppError(403, "FORBIDDEN", "접근 권한이 없습니다.")


def invalid_status() -> AppError:
    return AppError(422, "INVALID_STATUS", "유효하지 않은 상태값입니다.")


def invalid_payload(message: str = "요청이 올바르지 않습니다.") -> AppError:
    return AppError(422, "INVALID_PAYLOAD", message)
