import streamlit as st
from databricks import sql
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabricksDatabase:
    def __init__(self):
        try:
            self.host = st.secrets["DATABRICKS_HOST"]
            self.http_path = st.secrets["DATABRICKS_HTTP_PATH"]
            self.token = st.secrets["DATABRICKS_TOKEN"]
            self.database = st.secrets.get("DATABASE_NAME", "insurance_db")
            self.table = st.secrets.get("TABLE_NAME", "insurance_data")
            logger.info(f"✅ Policyholder DB config: {self.database}.{self.table}")
        except Exception as e:
            logger.error(f"❌ Failed to load Databricks secrets: {e}")
    
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
            logger.error(f"❌ Databricks connection failed: {e}")
            return None
    
    def authenticate_policyholder(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Authenticate policyholder using REAL Databricks data"""
        try:
            conn = self.get_connection()
            if not conn:
                return None
            
            with conn.cursor() as cursor:
                query = f"""
                SELECT 
                    EmployeeID,
                    FirstName,
                    LastName,
                    Email,
                    PolicyNumber,
                    PolicyStatus,
                    CoverageAmountUSD
                FROM {self.database}.{self.table}
                WHERE EmployeeID = ?
                   OR Email = ? 
                   OR PolicyNumber = ?
                LIMIT 1
                """
                
                cursor.execute(query, (identifier, identifier, identifier))
                result = cursor.fetchone()
                
                if result:
                    user_data = {
                        "employee_id": result[0],
                        "first_name": result[1],
                        "last_name": result[2],
                        "email": result[3],
                        "policy_number": result[4],
                        "policy_status": result[5],
                        "coverage_amount": float(result[6]) if result[6] else 0,
                        "role": "policyholder",
                        "is_admin": False
                    }
                    return user_data
                return None
                
        except Exception as e:
            logger.error(f"Policyholder auth error: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_policyholder_claims(self, employee_id: str) -> list:
        """Get claims for policyholder"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                query = f"""
                SELECT 
                    ClaimDate,
                    ClaimStatus,
                    LastClaimAmountUSD,
                    FraudRisk
                FROM {self.database}.{self.table}
                WHERE EmployeeID = ?
                ORDER BY ClaimDate DESC
                LIMIT 10
                """
                cursor.execute(query, (employee_id,))
                results = cursor.fetchall()
                
                claims = []
                for row in results:
                    claims.append({
                        "date": row[0],
                        "status": row[1],
                        "amount": float(row[2]) if row[2] else 0,
                        "fraud_risk": row[3]
                    })
                return claims
        except Exception as e:
            logger.error(f"Error getting claims: {e}")
            return []

# Create instance - THIS IS IMPORTANT!
policyholder_db = DatabricksDatabase()
