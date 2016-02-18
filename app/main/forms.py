# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import FloatField,IntegerField,StringField,SubmitField,TextAreaField,TextField,SelectField,FileField,SelectMultipleField,BooleanField,PasswordField
from wtforms import validators,ValidationError
from ..models import User

class LoginForm(Form):
	email = StringField("邮箱地址:",[validators.Required()])
	password = PasswordField('密码:',[validators.Required()])
	submit = SubmitField("提交")

class RegisterForm(Form):
	email = StringField("邮箱地址:",[validators.Required()])
	password = PasswordField('密码:',[validators.Required()])
	confirmpass = PasswordField('确认密码:',[validators.EqualTo('password',message='两次密码输入不一致')])
	submit = SubmitField("提交")

	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError("该邮箱已注册")

if __name__ == '__main__':
	print('ok')
