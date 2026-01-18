import streamlit as st
from databricks import sql
import pandas as pd
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabricksDatabase:
    def __init__(self):
        self.host = st.secrets["DATABRICKS_HOST"]
        self.http_path = st.secrets["DATABRICKS_HTTP_PATH"]
        self.token = st.secrets["DATABRICKS_TOKEN"]
        self.database = st.secrets.get("DATABASE_NAME", "insurance_db")
        self.table = st.secrets.get("TABLE_NAME", "insurance_data")
        
    def get_connection(self):
        """Create Databricks SQL connection"""
        try:
            conn = sql.connect(
                server_hostname=self.host,
                http_path=self.http_path,
                access_token=self.token
            )
            return conn
        except Exception as e:
            logger.error(f"Databricks connection failed: {e}")
            return None
    
    def authenticate_user(self, identifier: str, password: str = None) -> Optional[Dict[str, Any]]:
        """Authenticate user using REAL Databricks data"""
        try:
            conn = self.get_connection()
            if not conn:
                return None
            
            with conn.cursor() as cursor:
                # Query to find user by EmployeeID, Email, or PolicyNumber
                query = f"""
                SELECT 
                    EmployeeID,
                    FirstName,
                    LastName,
                    Email,
                    Phone,
                    PolicyNumber,
                    InsuranceType,
                    PolicyStatus,
                    CoverageAmountUSD,
                    MonthlyPremiumUSD,
                    ClaimStatus,
                    RiskScore,
                    FraudRisk,
                    Company,
                    Role
                FROM {self.database}.{self.table}
                WHERE EmployeeID = %s 
                   OR Email = %s 
                   OR PolicyNumber = %s
                LIMIT 1
                """
                
                cursor.execute(query, (identifier, identifier, identifier))
                result = cursor.fetchone()
                
                if result:
                    # Map result to user dictionary
                    user_data = {
                        "employee_id": result[0],
                        "first_name": result[1],
                        "last_name": result[2],
                        "email": result[3],
                        "phone": result[4],
                        "policy_number": result[5],
                        "insurance_type": result[6],
                        "policy_status": result[7],
                        "coverage_amount": float(result[8]) if result[8] else 0,
                        "monthly_premium": float(result[9]) if result[9] else 0,
                        "claim_status": result[10],
                        "risk_score": int(result[11]) if result[11] else 0,
                        "fraud_risk": result[12],
                        "company": result[13],
                        "role": result[14],
                        "auth_method": "databricks"
                    }
                    return user_data
                return None
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_user_policies(self, employee_id: str) -> list:
        """Get all policies for a user"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                query = f"""
                SELECT 
                    PolicyNumber,
                    InsuranceType,
                    CoverageCategory,
                    PlanType,
                    PolicyStatus,
                    PolicyStartDate,
                    PolicyEndDate,
                    CoverageAmountUSD,
                    MonthlyPremiumUSD
                FROM {self.database}.{self.table}
                WHERE EmployeeID = %s
                """
                cursor.execute(query, (employee_id,))
                results = cursor.fetchall()
                
                policies = []
                for row in results:
                    policies.append({
                        "policy_number": row[0],
                        "insurance_type": row[1],
                        "coverage_category": row[2],
                        "plan_type": row[3],
                        "policy_status": row[4],
                        "start_date": row[5],
                        "end_date": row[6],
                        "coverage_amount": float(row[7]) if row[7] else 0,
                        "monthly_premium": float(row[8]) if row[8] else 0
                    })
                return policies
        except Exception as e:
            logger.error(f"Error getting policies: {e}")
            return []
    
    def get_user_claims(self, employee_id: str) -> list:
        """Get claim history for user"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                query = f"""
                SELECT 
                    PolicyNumber,
                    ClaimStatus,
                    ClaimDate,
                    LastClaimAmountUSD,
                    FraudRisk,
                    PreviousClaims,
                    ClaimFrequency
                FROM {self.database}.{self.table}
                WHERE EmployeeID = %s
                ORDER BY ClaimDate DESC
                """
                cursor.execute(query, (employee_id,))
                results = cursor.fetchall()
                
                claims = []
                for row in results:
                    claims.append({
                        "policy_number": row[0],
                        "status": row[1],
                        "date": row[2],
                        "amount": float(row[3]) if row[3] else 0,
                        "fraud_risk": row[4],
                        "previous_claims": int(row[5]) if row[5] else 0,
                        "claim_frequency": float(row[6]) if row[6] else 0
                    })
                return claims
        except Exception as e:
            logger.error(f"Error getting claims: {e}")
            return []
    
    def get_user_health_profile(self, employee_id: str) -> Dict[str, Any]:
        """Get health profile for user"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                query = f"""
                SELECT 
                    ChronicCondition,
                    Smoker,
                    Alcoholic,
                    BMICategory,
                    BloodPressure,
                    PreviousHospitalizations,
                    RiskScore
                FROM {self.database}.{self.table}
                WHERE EmployeeID = %s
                LIMIT 1
                """
                cursor.execute(query, (employee_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        "chronic_condition": result[0],
                        "smoker": result[1],
                        "alcoholic": result[2],
                        "bmi_category": result[3],
                        "blood_pressure": result[4],
                        "hospitalizations": int(result[5]) if result[5] else 0,
                        "risk_score": int(result[6]) if result[6] else 0
                    }
                return {}
        except Exception as e:
            logger.error(f"Error getting health profile: {e}")
            return {}

# Global database instance
db = DatabricksDatabase()
