# scripts/download_model.py
from huggingface_hub import snapshot_download
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--repo", default="neuralmind/bert-base-portuguese-cased")
parser.add_argument("--out", default="models/transformer/bert-base-portuguese-cased")
args = parser.parse_args()

print("Downloading model from", args.repo)
snapshot_download(repo_id=args.repo, local_dir=args.out, repo_type="model")
print("Downloaded to", args.out)
