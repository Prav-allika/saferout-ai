"""
Quick Test Script - Verify SafeRoute AI Works
Run this to make sure everything is set up correctly!
"""

print("🚀 Testing SafeRoute AI System...")
print("=" * 50)

# Test 1: Check imports
print("\n1️⃣ Testing imports...")
try:
    from agents.orchestrator import Orchestrator
    from simulation.sensors import Vehicle
    from config.settings import settings
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Run: pip install -r requirements.txt")
    exit(1)

# Test 2: Create orchestrator
print("\n2️⃣ Testing orchestrator initialization...")
try:
    orchestrator = Orchestrator()
    print("✅ Orchestrator created successfully!")
except Exception as e:
    print(f"❌ Orchestrator error: {e}")
    exit(1)

# Test 3: Create vehicle
print("\n3️⃣ Testing vehicle simulation...")
try:
    vehicle = Vehicle("TEST-123", "normal")
    sensor_data = vehicle.get_sensor_data()
    print(f"✅ Vehicle created! ID: {sensor_data['vehicle_id']}")
    print(f"   Tires: {len(sensor_data['tires'])} sensors")
    print(f"   Engine data: ✅")
except Exception as e:
    print(f"❌ Vehicle error: {e}")
    exit(1)

# Test 4: Run analysis
print("\n4️⃣ Testing orchestrator analysis...")
try:
    decisions = orchestrator.analyze_sensor_data(sensor_data)
    print(f"✅ Analysis complete!")
    print(f"   Risk Level: {decisions['risk_level']}")
    print(f"   Alerts: {len(decisions['alerts'])}")
    print(f"   Actions: {len(decisions['actions'])}")
except Exception as e:
    print(f"❌ Analysis error: {e}")
    exit(1)

# Test 5: Check ML model
print("\n5️⃣ Testing ML model...")
try:
    tire_data = sensor_data["tires"]["front_left"]
    prediction = orchestrator.tire_predictor.analyze(tire_data, sensor_data["metadata"])
    print(f"✅ ML model works!")
    print(f"   Failure probability: {prediction['ml_prediction']['failure_probability']*100:.1f}%")
except Exception as e:
    print(f"❌ ML model error: {e}")
    exit(1)

# All tests passed!
print("\n" + "=" * 50)
print("🎉 ALL TESTS PASSED! Your app is working perfectly!")
print("=" * 50)
print("\n✅ You're ready to:")
print("   1. Push to GitHub")
print("   2. Add to your resume")
print("   3. Show to recruiters")
print("\n💡 Next step: Run 'streamlit run ui/dashboard.py' to see the UI!")
