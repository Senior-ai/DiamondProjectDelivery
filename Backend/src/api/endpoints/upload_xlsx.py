from typing import Union, Optional
from fastapi import Depends, HTTPException, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
import pandas as pd
from io import BytesIO

from ..router import router
from ...core import BACKEND_ACCESS_TOKEN

bearer = HTTPBearer()

@router.post('/upload_xlsx', response_class=StreamingResponse)
async def upload_xlsx(
        token: HTTPAuthorizationCredentials = Depends(bearer),
        file: UploadFile = File(...)
) -> StreamingResponse:
    # Check token credentials
    if token.credentials != BACKEND_ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    # Read the XLSX file content
    content = await file.read()
    xlsx_file = BytesIO(content)

    # Convert the XLSX file to CSV using pandas
    df = pd.read_excel(xlsx_file, engine='openpyxl')
    csv_data = df.to_csv(index=False)

    # Create a streaming response with the CSV data
    response = StreamingResponse(
        BytesIO(csv_data.encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={file.filename.split('.')[0]}.csv"
        }
    )

    return response