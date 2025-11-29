from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Literal, Annotated
import pickle
import pandas as pd

# import the ml model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# define model version
MODEL_VERSION = "1.0.0"

# create the fastapi app
app =FastAPI()


#pydantic model to validate the incoming data
class UserInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the user in years")] 
    weight: Annotated[float, Field(..., gt=0, description="weight of the user in years")] 
    height: Annotated[float, Field(..., gt=0, description="weight of the user in meters")]
    income: Annotated[float, Field(..., gt=0, description="Annual salary of the user in LPA")]
    smoker: Annotated[bool, Field(..., description="is user a smoker or not")]
    city: Annotated[str, Field(...,description=" The city that the user belongs to")]
    occupation: Annotated[Literal['Software Engineer', 'Teacher', 'Doctor', 'Nurse',
       'Business Owner', 'Police Officer', 'Student', 'Engineer',
       'Accountant', 'Lawyer'], Field(..., description="Occupation of the user")]
    
    @field_validator('city')
    @classmethod
    def normalize_city(cls, value):
        return value.strip().title()
    
    
    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight / (self.height ** 2)
    
    @computed_field
    @property
    def lifestyle_risk(self) -> int:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker or self.bmi >27:
            return "medium"
        else:
            return "low"
        
    @computed_field
    @property
    def age_group(self) -> str:
            if self.age < 25:
                return "young"
            elif self.age < 45:
                return "adult"
            elif self.age < 60:
                return "middle_aged"
            return "senior"
        
    @computed_field
    @property
    def city_tier(self) -> int:
        tier_1_cities = ["Mumbai, Delhi, Bengaluru, Chennai, Kolkata, Hyderabad, Ahmedabad, Pune"]
        tier_2_cities = ["jaipur, Lucknow, Kanpur, Chandigarh, Amritsar, Varanasi, Allahabad, Agra, Dehradun, Jammu, Patna, Ranchi, Bhubaneswar, Guwahati, Jamshedpur, Dhanbad, Siliguri, Gwalior, Jabalpur, Raipur, Bilaspur"]

        def city_tier(city):
            if self.city in tier_1_cities:
                return "tier_1"
            elif self.city in tier_2_cities:
                return "tier_2"
            else:
                return "tier_3"



# create a home endpoint (Human readable)
@app.get("/")
def home():
    return {"message": "Welcome to the Insurance Premium Category Prediction API"}


# create a health check endpoint (Machine readable; to deploy in cloud services.)
@app.get("/health")
def health_check():
    return {"status": "API is healthy and running",
            "version": MODEL_VERSION,
            "model_loaded": model is not None}


# create the prediction endpoint 
@app.post("/predict")  
def predict_premium(data: UserInput):


# prepare the input data for prediction
    input_df = pd.DataFrame([{
        'bmi': data.bmi,
        'age_group': data.age_group,
        'city_tier': data.city_tier,
        'lifestyle_risk': data.lifestyle_risk,
        'occupation': data.occupation,
        'income_lpa': data.income 
    }])
    
    prediction = model.predict(input_df)[0]

    return JSONResponse(status_code = 200,content={"predicted_category": prediction})