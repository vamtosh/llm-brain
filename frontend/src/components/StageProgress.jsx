import './StageProgress.css';

export default function StageProgress({ currentStage }) {
  const stages = [
    { name: 'WIDEN', value: 'widen', icon: '🔍', description: 'Explore Problem Space' },
    { name: 'DIAGNOSE', value: 'diagnose', icon: '🔬', description: 'Analyze Root Causes' },
    { name: 'CONVERGE', value: 'converge', icon: '💡', description: 'Generate Solutions' },
    { name: 'SELECT', value: 'select_solution', icon: '📋', description: 'Choose Solution' },
    { name: 'PRD', value: 'generate_prd', icon: '📄', description: 'Generate PRD' },
  ];

  const getStageStatus = (stageValue) => {
    const stageIndex = stages.findIndex(s => s.value === stageValue);
    const currentIndex = stages.findIndex(s => s.value === currentStage);

    if (stageIndex < currentIndex) return 'completed';
    if (stageIndex === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="stage-progress">
      {stages.map((stage, index) => {
        const status = getStageStatus(stage.value);
        return (
          <div key={stage.value} className="stage-progress-container">
            <div className={`stage-indicator ${status}`}>
              <div className="stage-icon">{stage.icon}</div>
              <div className="stage-name">{stage.name}</div>
              <div className="stage-description">{stage.description}</div>
              {status === 'completed' && <div className="checkmark">✓</div>}
              {status === 'active' && <div className="pulse"></div>}
            </div>
            {index < stages.length - 1 && (
              <div className={`stage-connector ${status === 'completed' ? 'completed' : ''}`}></div>
            )}
          </div>
        );
      })}
    </div>
  );
}
