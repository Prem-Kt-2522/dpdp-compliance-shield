import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from analyzer import scan_text_for_pii

def scan_s3_bucket(access_key, secret_key, bucket_name, region):
    """
    Connects to an AWS S3 Bucket, reads text/csv/sql files, and scans for PII.
    """
    findings = []
    
    try:
        # 1. Establish Connection to AWS
        print(f"[*] Connecting to AWS S3 Bucket: {bucket_name}...")
        s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # 2. List Files (Limit to first 20 for the demo to be fast)
        response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=20)

        if 'Contents' not in response:
            return {"error": "Bucket is empty or not accessible."}

        # 3. Iterate and Scan
        for item in response['Contents']:
            file_key = item['Key']
            
            # Only scan text-based files
            if file_key.endswith(('.csv', '.txt', '.sql', '.json', '.log')):
                print(f"[*] Scanning Cloud Object: {file_key}")
                
                try:
                    # Download file content into RAM (Streaming)
                    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
                    content = obj['Body'].read().decode('utf-8', errors='ignore')
                    
                    # Split into lines and scan
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        leaks = scan_text_for_pii(line, line_number=f"S3: {file_key} -> Line {i+1}")
                        findings.extend(leaks)
                        
                except Exception as e:
                    print(f"[!] Could not read {file_key}: {e}")
                    continue

    except NoCredentialsError:
        return {"error": "Invalid AWS Credentials."}
    except ClientError as e:
        return {"error": f"AWS Error: {e.response['Error']['Message']}"}
    except Exception as e:
        return {"error": str(e)}

    return findings