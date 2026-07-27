import { useState } from "react";
import type { TreeNodeData } from "../api/types";

interface Props {
  node: TreeNodeData;
  depth: number;
  onSelectClass: (ifcClass: string) => void;
  defaultOpen?: boolean;
}

export default function TreeNode({ node, depth, onSelectClass, defaultOpen = false }: Props) {
  const [open, setOpen] = useState(defaultOpen || depth === 0);
  const hasChildren = node.children.length > 0;

  const label =
    node.type === "class" && node.class_fr ? `${node.name} — ${node.class_fr}` : node.name;

  return (
    <div className="tree-node">
      <div
        className="tree-node__row"
        onClick={() => {
          if (node.type === "class" && node.ifc_class) {
            onSelectClass(node.ifc_class);
          } else if (hasChildren) {
            setOpen((v) => !v);
          }
        }}
      >
        {hasChildren ? (
          <button
            className="tree-node__toggle"
            aria-label={open ? "Réduire" : "Développer"}
            onClick={(e) => {
              e.stopPropagation();
              setOpen((v) => !v);
            }}
          >
            {open ? "▾" : "▸"}
          </button>
        ) : (
          <span className="tree-node__toggle" />
        )}
        <span className={`tree-node__label tree-node__label--${node.type}`}>{label}</span>
      </div>
      {open && hasChildren && (
        <div className="tree-node__children">
          {node.children.map((child) => (
            <TreeNode
              key={child.name}
              node={child}
              depth={depth + 1}
              onSelectClass={onSelectClass}
            />
          ))}
        </div>
      )}
    </div>
  );
}
