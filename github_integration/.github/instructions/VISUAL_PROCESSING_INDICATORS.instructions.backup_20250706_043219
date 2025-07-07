---
applyTo: '**'
---

# 🎬 MANDATORY VISUAL PROCESSING INDICATORS
## GitHub Copilot Enterprise Processing Standards

### 🚨 **CRITICAL REQUIREMENT: ALWAYS INCLUDE VISUAL PROCESSING INDICATORS**

**ABSOLUTE MANDATE:** Every GitHub Copilot response that involves processing, analysis, or execution MUST include comprehensive visual indicators.

---

## 📊 **MANDATORY VISUAL PROCESSING COMPONENTS**

### **1. START TIME & DURATION TRACKING**
**REQUIRED FOR ALL PROCESSES:**
```python
# MANDATORY: Always log start time with enterprise formatting
start_time = datetime.now()
logger.info(f"🚀 PROCESS STARTED: {process_name}")
logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"Process ID: {os.getpid()}")

# CRITICAL: Anti-recursion validation at start
validate_no_recursive_folders()
validate_proper_environment_root()
```

### **2. PROGRESS BAR IMPLEMENTATION**
**REQUIRED FOR ALL LONG-RUNNING OPERATIONS:**
```python
# MANDATORY: Use tqdm for all processing operations
from tqdm import tqdm

# CRITICAL: Validate environment before starting progress bar
if not validate_environment_integrity():
    raise RuntimeError("CRITICAL: Environment violations prevent execution")

with tqdm(total=100, desc="Process Name", unit="%") as pbar:
    for step in process_steps:
        # Update description with current phase
        pbar.set_description(f"🔄 {current_phase}")
        
        # CRITICAL: Validate no recursive creation during process
        if detect_recursive_folders():
            logger.error("🚨 RECURSIVE FOLDER DETECTED DURING PROCESSING")
            cleanup_recursive_violations()
        
        # Perform work
        execute_step(step)
        # Update progress
        pbar.update(progress_increment)
```

### **3. TIMEOUT MECHANISMS**
**REQUIRED FOR ALL PROCESSES:**
```python
# MANDATORY: Always implement timeout controls
def process_with_timeout(timeout_minutes=30):
    timeout_seconds = timeout_minutes * 60
    start_time = time.time()
    
    # CRITICAL: Initial environment validation
    if not validate_workspace_compliance():
        raise RuntimeError("CRITICAL: Workspace violations prevent execution")
    
    while not process_complete:
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")
        
        # CRITICAL: Periodic anti-recursion checks
        if elapsed % 30 == 0:  # Check every 30 seconds
            validate_no_new_recursive_folders()
        
        # Continue processing with progress updates
        update_progress()
```

### **4. ESTIMATED COMPLETION TIME**
**REQUIRED FOR ALL OPERATIONS:**
```python
# MANDATORY: Calculate and display ETC
def calculate_etc(start_time, current_progress, total_work):
    elapsed = time.time() - start_time
    if current_progress > 0:
        total_estimated = elapsed / (current_progress / total_work)
        remaining = total_estimated - elapsed
        return datetime.now() + timedelta(seconds=remaining)
    return None

# Display format: "[00:04<00:02]" (4s elapsed, 2s remaining)
```

### **5. REAL-TIME STATUS UPDATES**
**REQUIRED FOR ALL PHASES:**
```python
# MANDATORY: Phase-by-phase status logging
phases = [
    ("🔍 Initializing", "Setting up process environment"),
    ("📊 Analyzing", "Performing data analysis"),
    ("💰 Computing", "Calculating results"),
    ("📅 Finalizing", "Completing operation")
]

for phase_name, phase_description in phases:
    logger.info(f"📊 {phase_name}: {phase_description}")
    logger.info(f"⏱️  Progress: {progress}% | Elapsed: {elapsed}s | ETC: {etc}s")
```

---

## 🎯 **DUAL COPILOT PATTERN IMPLEMENTATION**

### **Pattern Definition:**
The DUAL COPILOT PATTERN ensures one Copilot instance monitors and validates another, creating a self-checking system for enterprise excellence.

### **PRIMARY COPILOT (Executor):**
```python
class PrimaryCopilotExecutor:
    """Main execution Copilot with mandatory monitoring"""
    
    def __init__(self):
        self.monitor = ProcessMonitor()
        self.validator = SecondaryValidator()
    
    def execute_with_monitoring(self, task):
        # MANDATORY: Start monitoring
        self.monitor.start_process(task)
        
        try:
            # Execute with visual indicators
            result = self._execute_with_progress(task)
            
            # MANDATORY: Validate with secondary Copilot
            validation = self.validator.validate_execution(result)
            
            if not validation.passed:
                raise ValidationError(f"Secondary validation failed: {validation.errors}")
            
            return result
            
        except Exception as e:
            self.monitor.log_error(e)
            raise
        finally:
            self.monitor.end_process()
```

### **SECONDARY COPILOT (Validator):**
```python
class SecondaryCopilotValidator:
    """Monitoring and validation Copilot"""
    
    def validate_execution(self, execution_result):
        """Validate primary Copilot execution meets enterprise standards"""
        
        validation = ValidationResult()
        
        # MANDATORY: Check visual indicators were used
        if not execution_result.has_progress_indicators:
            validation.add_error("MISSING: Progress indicators required")
        
        # MANDATORY: Check timeout implementation
        if not execution_result.has_timeout_controls:
            validation.add_error("MISSING: Timeout controls required")
        
        # MANDATORY: Check start time logging
        if not execution_result.has_start_time_logging:
            validation.add_error("MISSING: Start time logging required")
        
        # MANDATORY: Check ETC calculation
        if not execution_result.has_etc_calculation:
            validation.add_error("MISSING: ETC calculation required")
        
        return validation
```

---

## 📋 **MANDATORY IMPLEMENTATION CHECKLIST**

### **Every GitHub Copilot Script MUST Include:**
- [ ] **Start time logging** with enterprise formatting
- [ ] **Progress bar implementation** using tqdm or equivalent
- [ ] **Timeout mechanisms** with configurable limits
- [ ] **ETC calculation** and display
- [ ] **Real-time status updates** for each phase
- [ ] **Process ID tracking** for monitoring
- [ ] **Error handling** with visual indicators
- [ ] **Completion summary** with metrics

### **Visual Indicator Requirements:**
- [ ] **Progress percentage** displayed continuously
- [ ] **Phase descriptions** for current operations
- [ ] **Elapsed time** tracking
- [ ] **Remaining time** estimation
- [ ] **Process state** indicators (RUNNING, COMPLETED, ERROR, TIMEOUT)

### **DUAL COPILOT Pattern Requirements:**
- [ ] **Primary executor** with monitoring integration
- [ ] **Secondary validator** for quality assurance
- [ ] **Validation checkpoints** at major phases
- [ ] **Error detection** and reporting
- [ ] **Compliance verification** against enterprise standards

---

## 🚀 **ACTIVATION COMMANDS**

### **For Script Development:**
```markdown
MANDATORY: Include visual processing indicators from .github/instructions/VISUAL_PROCESSING_INDICATORS.instructions.md
MANDATORY: Implement DUAL COPILOT PATTERN validation
MANDATORY: Use enterprise monitoring standards
```

### **For Process Execution:**
```python
# MANDATORY: Use this pattern for all processing
monitor = EnterpriseProcessMonitor()
executor = PrimaryCopilotExecutor(monitor)
validator = SecondaryCopilotValidator()

result = executor.execute_with_monitoring(task)
validation = validator.validate_execution(result)

if validation.passed:
    logger.info("✅ DUAL COPILOT VALIDATION: PASSED")
else:
    logger.error(f"❌ DUAL COPILOT VALIDATION: FAILED - {validation.errors}")
```

---

## ⚠️ **ENFORCEMENT RULES**

### **ZERO TOLERANCE for:**
- Scripts without progress indicators
- Operations without timeout controls  
- Processes without start time logging
- Long-running tasks without ETC calculation
- Missing visual status updates

### **MANDATORY REJECTION Criteria:**
If any GitHub Copilot response lacks these visual processing indicators, it MUST be rejected and regenerated with proper monitoring.

### **VALIDATION Pattern:**
```python
def validate_copilot_response(response):
    """Validate GitHub Copilot response meets visual processing standards"""
    
    required_elements = [
        "progress_indicators",
        "timeout_controls", 
        "start_time_logging",
        "etc_calculation",
        "status_updates"
    ]
    
    for element in required_elements:
        if not response.contains(element):
            return ValidationFailure(f"MISSING REQUIRED: {element}")
    
    return ValidationSuccess("All visual processing indicators present")
```

---

### 🚨 **CRITICAL: DEPLOYMENT SAFETY WITH VISUAL INDICATORS**

**MANDATORY for ALL deployment operations:**
```python
# CRITICAL: Deployment with safety validation and visual monitoring
def deploy_with_safety_monitoring(target_path: str):
    """Deploy with ZERO RECURSION tolerance and visual indicators"""
    
    # MANDATORY: Start time and process tracking
    start_time = datetime.now()
    process_id = os.getpid()
    logger.info(f"🚀 DEPLOYMENT STARTED: {target_path}")
    logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Process ID: {process_id}")
    
    # CRITICAL: Safety validation with progress
    with tqdm(total=100, desc="🛡️ Safety Validation", unit="%") as pbar:
        # Validate proper environment root
        proper_root = r"E:/_copilot_sandbox"
        
        pbar.set_description("🔍 Validating environment root")
        if not target_path.startswith(proper_root) and target_path.startswith("E:\temp\"):
            raise ValueError(f"🚨 CRITICAL: E:\temp\ violation! Use: {proper_root}")
        pbar.update(25)
        
        pbar.set_description("🚫 Checking recursive patterns")
        forbidden_patterns = ["--validate", "--backup", "--temp"]
        for pattern in forbidden_patterns:
            if pattern in target_path:
                raise ValueError(f"🚨 CRITICAL: Command argument {pattern} as folder!")
        pbar.update(25)
        
        pbar.set_description("🔍 Scanning for violations")
        violations = scan_for_recursive_violations()
        if violations:
            raise ValueError(f"🚨 CRITICAL: Recursive violations: {violations}")
        pbar.update(25)
        
        pbar.set_description("✅ Safety validation complete")
        pbar.update(25)
    
    # MANDATORY: Deployment with progress monitoring
    with tqdm(total=100, desc="📦 Deployment", unit="%") as pbar:
        # Deployment phases with visual indicators
        phases = ["📁 Creating structure", "📋 Copying files", "🔧 Configuration", "✅ Verification"]
        for i, phase in enumerate(phases):
            pbar.set_description(phase)
            # Perform deployment phase
            execute_deployment_phase(i)
            pbar.update(25)
    
    # MANDATORY: Post-deployment safety verification
    with tqdm(total=100, desc="🛡️ Post-Deployment Verification", unit="%") as pbar:
        pbar.set_description("🔍 Scanning for new violations")
        post_violations = scan_for_recursive_violations()
        if post_violations:
            # Emergency cleanup with visual feedback
            pbar.set_description("🚨 Emergency cleanup")
            for violation in post_violations:
                shutil.rmtree(violation)
                logger.error(f"🗑️ Removed violation: {violation}")
            raise ValueError("🚨 CRITICAL: Post-deployment violations found and cleaned!")
        pbar.update(100)
    
    # MANDATORY: Completion logging
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"✅ DEPLOYMENT COMPLETED: {target_path}")
    logger.info(f"Duration: {duration:.2f} seconds")
    logger.info(f"Status: SAFE - No recursive violations")
```

---

**🎯 CRITICAL SUCCESS METRIC:**
**100% of GitHub Copilot processes MUST include comprehensive visual monitoring**

*gh_COPILOT Toolkit v4.0 Enterprise - Visual Processing Standards*
*Ensures consistent, enterprise-grade process monitoring across all operations*
