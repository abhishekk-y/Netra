"""Train a GRU from supplied stage windows; no random synthetic training data."""
import argparse
import numpy as np
import torch
from ml.models.sequence_model import SequenceForecaster


def main():
    parser = argparse.ArgumentParser(description="Train GRU on NPZ X[N,T] (0 padding, stages 1..K), y[N] (0..K-1)")
    parser.add_argument("--data", required=True)
    parser.add_argument("--num-stages", required=True, type=int)
    parser.add_argument("--epochs", default=5, type=int)
    parser.add_argument("--output", default="sequence_model.pt")
    args = parser.parse_args()
    with np.load(args.data, allow_pickle=False) as data:
        X, y = torch.as_tensor(data["X"], dtype=torch.long), torch.as_tensor(data["y"], dtype=torch.long)
    if X.ndim != 2 or y.shape != (len(X),) or not len(X) or X.shape[1] == 0:
        parser.error("Expected nonempty X[N,T] and y[N]")
    if args.num_stages < 2 or args.epochs < 1 or X.min() < 0 or X.max() > args.num_stages or y.min() < 0 or y.max() >= args.num_stages:
        parser.error("Invalid stage indices, stage count, or epoch count")
    torch.manual_seed(42)
    model = SequenceForecaster(args.num_stages)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.CrossEntropyLoss()
    loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(X, y), batch_size=64, shuffle=False)
    for epoch in range(args.epochs):
        model.train()
        losses = []
        for batch, labels in loader:
            optimizer.zero_grad()
            logits, _ = model(batch)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        print(f"Epoch {epoch+1}: training loss {np.mean(losses):.6f}")
    model.save(args.output)
    print(f"Saved {args.output}; training loss is not held-out forecast accuracy.")


if __name__ == "__main__":
    main()
