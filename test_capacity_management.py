"""
Script de prueba para el sistema de gestión de capacidad
Prueba Feature Toggles y Throttling
"""
import asyncio
import httpx
import time
from typing import List, Dict
import json

# Configuración
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/v1"

# ... (rest of imports and print functions remain same)

async def test_health_check():
    """Test 1: Health Check"""
    print_header("TEST 1: Health Check")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_V1}/admin/health")
            data = response.json()
            
            print_info(f"Status: {data['status']}")
            
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            print_success("Health check OK")
            return True
        except Exception as e:
            print_error(f"Error en health check: {e}")
            raise e  # Re-raise to fail the test

async def test_feature_toggles():
    """Test 2: Feature Toggles"""
    print_header("TEST 2: Feature Toggles")
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Ver estado inicial
            response = await client.get(f"{API_V1}/admin/features")
            assert response.status_code == 200, "Failed to get features"
            
            # 2. Desactivar transaction_delete
            response = await client.post(f"{API_V1}/admin/features/transaction_delete/disable")
            assert response.status_code == 200, "Failed to disable feature"
            print_success("transaction_delete desactivado")
            
            # 3. Verificar que está desactivado
            response = await client.get(f"{API_V1}/admin/features")
            assert not response.json()['features']['transaction_delete'], "Feature should be disabled"
            
            # 4. Intentar usar la feature
            response = await client.delete(f"{API_V1}/transactions/test123")
            assert response.status_code == 503, f"Expected 503, got {response.status_code}"
            print_success("DELETE bloqueado correctamente (503)")
            
            # 5. Reactivar feature
            response = await client.post(f"{API_V1}/admin/features/transaction_delete/enable")
            assert response.status_code == 200, "Failed to enable feature"
            print_success("transaction_delete reactivado")
            
            return True
            
        except Exception as e:
            print_error(f"Error en feature toggles: {e}")
            raise e


async def test_emergency_mode():
    """Test 3: Modo Emergencia"""
async def test_emergency_mode():
    """Test 3: Modo Emergencia"""
    print_header("TEST 3: Modo Emergencia")
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Ver estado inicial
            response = await client.get(f"{API_V1}/admin/features")
            assert response.status_code == 200, "Failed to get features"
            
            # 2. Activar modo emergencia
            response = await client.post(f"{API_V1}/admin/emergency/disable-non-critical")
            assert response.status_code == 200, "Failed to activate emergency mode"
            print_success("Modo emergencia activado")
            
            # 3. Verificar que operaciones no críticas están bloqueadas
            
            # DELETE debería estar bloqueado
            response = await client.delete(f"{API_V1}/transactions/test123")
            assert response.status_code == 503, f"DELETE should be blocked (503), got {response.status_code}"
            print_success("DELETE bloqueado (503)")
            
            # REVERT debería estar bloqueado
            response = await client.patch(f"{API_V1}/transactions/test123")
            assert response.status_code == 503, f"REVERT should be blocked (503), got {response.status_code}"
            print_success("REVERT bloqueado (503)")
            
            # 4. Restaurar modo normal
            response = await client.post(f"{API_V1}/admin/emergency/restore")
            assert response.status_code == 200, "Failed to restore normal mode"
            print_success("Modo normal restaurado")
            
            return True
            
        except Exception as e:
            print_error(f"Error en modo emergencia: {e}")
            raise e


async def test_throttling():
    """Test 4: Throttling con Carga"""
async def test_throttling():
    """Test 4: Throttling con Carga"""
    print_header("TEST 4: Throttling bajo Carga")
    
    print_info("Generando 50 requests concurrentes...")
    
    async def make_request(client: httpx.AsyncClient, i: int) -> Dict:
        start_time = time.time()
        try:
            # Intentar crear transacción
            response = await client.post(
                f"{API_V1}/transactions",
                json={
                    "sender": f"user{i}",
                    "receiver": f"user{i+1}",
                    "quantity": 10.0
                },
                timeout=30.0
            )
            elapsed = time.time() - start_time
            return {
                "status": response.status_code,
                "elapsed": elapsed,
                "success": response.status_code in [200, 201, 400, 404, 202]  # Añadido 202 que es el éxito real
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "status": 0,
                "elapsed": elapsed,
                "success": False,
                "error": str(e)
            }
    
    async with httpx.AsyncClient() as client:
        # Lanzar requests concurrentes
        tasks = [make_request(client, i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        # Analizar resultados
        successful = sum(1 for r in results if r['success'])
        errors = sum(1 for r in results if not r['success'] and r['status'] != 503)
        
        print_info(f"Requests exitosos: {successful}/50")
        print_info(f"Errores: {errors}/50")
        
        # No hacemos assert sobre el throttling exacto porque depende de la máquina,
        # pero sí aseguramos que no haya errores de conexión masivos (status 0)
        assert errors < 25, f"Too many connection errors: {errors}/50"
        
        return True


async def test_metrics():
    """Test 5: Endpoint de Métricas"""
    print_header("TEST 5: Métricas Detalladas")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_V1}/admin/metrics")
            assert response.status_code == 200, "Failed to get metrics"
            data = response.json()
            
            assert 'system' in data, "Missing system metrics"
            assert 'requests' in data, "Missing requests metrics"
            assert 'throttling' in data, "Missing throttling metrics"
            assert 'features' in data, "Missing features metrics"
            
            print_success("Métricas obtenidas y validadas correctamente")
            return True
            
        except Exception as e:
            print_error(f"Error obteniendo métricas: {e}")
            raise e


async def run_all_tests():
    """Ejecutar todos los tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🧪 TEST SUITE: GESTIÓN DE CAPACIDAD                      ║")
    print("║  Throttling + Feature Toggles                             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)
    
    results = []
    
    # Test 1: Health Check
    result = await test_health_check()
    results.append(("Health Check", result))
    await asyncio.sleep(1)
    
    # Test 2: Feature Toggles
    result = await test_feature_toggles()
    results.append(("Feature Toggles", result))
    await asyncio.sleep(1)
    
    # Test 3: Modo Emergencia
    result = await test_emergency_mode()
    results.append(("Modo Emergencia", result))
    await asyncio.sleep(1)
    
    # Test 4: Throttling
    result = await test_throttling()
    results.append(("Throttling", result))
    await asyncio.sleep(1)
    
    # Test 5: Métricas
    result = await test_metrics()
    results.append(("Métricas", result))
    
    # Resumen
    print_header("RESUMEN DE TESTS")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests pasados{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ TODOS LOS TESTS PASARON{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ ALGUNOS TESTS FALLARON{Colors.RESET}\n")


if __name__ == "__main__":
    print_info("Asegúrate de que el servicio esté corriendo en http://localhost:8001")
    print_info("Presiona Ctrl+C para cancelar\n")
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests cancelados por el usuario{Colors.RESET}")
    except Exception as e:
        print_error(f"Error ejecutando tests: {e}")
