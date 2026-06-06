from src.auth.schemas import UserCreateModel

auth_prefix = f"/api/v1/auth"

def test_user_creation(fake_session, fake_user_service,test_client):
    signup_data = {
    	"username": "jasonher",
    	"email":"265905974444@qq.com",
    	"first_name":"666666",
    	"last_name":"666666",
    	"password":"12345678"
	}
    response = test_client.post(
		url=f"{auth_prefix}/signup", 
		json=signup_data
	)
    assert fake_user_service.user_exists_called_once()
    assert fake_user_service.user_exists_called_once_with(signup_data['email'],fake_session)
    assert fake_user_service.create_user_called_once()
    assert fake_user_service.create_user_called_once_with(UserCreateModel(**signup_data),fake_session)
