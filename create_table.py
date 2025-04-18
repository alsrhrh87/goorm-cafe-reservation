from database import metadata, engine

# 테이블 생성 (최초 1회만 실행하면 됨)
metadata.create_all(engine)

print("테이블 생성 완료")
