import secrets
import string

def generate_password(length=12):
    """
    장고 6.0의 보안 표준을 따르는 강력한 랜덤 패스워드 생성기.
    - 보안 컨설팅 전공자의 관점에서, 단순한 난수가 아닌 암호학적으로 안전한 secrets 모듈을 사용합니다.
    """
    # 영문 대소문자, 숫자, 특수문자를 모두 포함합니다.
    alphabet = string.ascii_letters + string.digits + string.punctuation
    
    # 암호학적으로 안전한(Cryptographically Secure) 랜덤 문자열을 생성합니다.
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    
    return password

# 💡 ID 생성기나 이메일 스레딩은 현재 UI 기획과 맞지 않아 삭제했습니다.
# 필요할 때 언제든 다시 'IPSE 스타일'로 깎아서 넣으면 되니까요!